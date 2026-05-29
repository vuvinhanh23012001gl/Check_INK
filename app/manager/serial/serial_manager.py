
import time
import queue
import threading
from queue import Queue
from .serial_connect import SerialConnect

class ManagerSerial:
    def __init__(
        self,
        serial_com: SerialConnect,
        queue_rx: Queue = None,
        queue_tx: Queue = None
    ):

        self.serial_com = serial_com
        self.rx_queue = queue_rx or Queue()
        self.tx_queue = queue_tx or Queue()


        self.running_rx = False
        self.running_tx = False
        self.running_check = True
        self.com_is_open = False
        self.rx_thread = None
        self.tx_thread = None

        self.check_thread = threading.Thread(
            target=self._check_connect,
            daemon=True,
            name="CheckCOM"
        )
        self.check_thread.start()


    def open_thread_receive_and_send(self):
        if self.running_rx or self.running_tx:
            return
        self.running_rx = True
        self.running_tx = True
        print("✅ Mở luồng RX/TX")
        self.rx_thread = threading.Thread(
            target=self._listen_serial,
            daemon=True,
            name="SerialRX"
        )
        self.tx_thread = threading.Thread(
            target=self._send_serial,
            daemon=True,
            name="SerialTX"
        )
        self.rx_thread.start()
        self.tx_thread.start()




    def close_thread_receive_and_send(self):
        print("🛑 Dừng luồng RX/TX")
        self.running_rx = False
        self.running_tx = False
        if self.rx_thread and self.rx_thread.is_alive():
            self.rx_thread.join(timeout=1)
            print("✅ Đã dừng RX")
        if self.tx_thread and self.tx_thread.is_alive():
            self.tx_thread.join(timeout=1)
            print("✅ Đã dừng TX")
        self.clear_rx_queue()
        self.clear_tx_queue()



    def _check_connect(self):
        # Cứ mỗi 2 s cập nhật lại kiểm tra kết nối với Com 1 lần.
        print("✅ Mở luồng check COM")
        while self.running_check:
            try:
                port_name = (
                    self.serial_com
                    .config
                    .device_port
                )
                if not port_name:
                    print("vao2")
                    time.sleep(1)
                    continue
                if not self.serial_com.check_port_exists(
                    port_name
                ):
                    if self.com_is_open:
                        print(
                            f"❌ Mất kết nối {port_name}"
                        )
                        self.com_is_open = False
                        self.serial_com.close_port()
                        self.close_thread_receive_and_send()
                    print("Cố gắng kết nối với COM ...")
                    time.sleep(1)
                    continue
                if (
                        not self.serial_com.ser
                        or not self.serial_com.ser.is_open
                    ):
                    print(
                        f"🔄 Đang mở {port_name}"
                    )
                    status = (
                        self.serial_com
                        .open_port()
                    )
                    if status:
                        print(
                            f"✅ Mở {port_name} thành công"
                        )
                        self.com_is_open = True
                        self.open_thread_receive_and_send()
                    else:
                        print(
                            f"❌ Không thể mở {port_name}"
                        )
                        self.com_is_open = False
                # print("Đã kết nối với COM")
                time.sleep(2)
            except Exception as e:
                print(
                    "[CheckCOM] Lỗi:",
                    e
                )
                time.sleep(2)



    def update_com(
        self,
        port_name,
        baudrate
    ) -> bool:
        print(
            f"🔄 Update COM: "
            f"{port_name} - {baudrate}"
        )
        self.close_thread_receive_and_send()
        self.serial_com.close_port()
        status = self.serial_com.open_manual(
            port_name,
            baudrate
        )
        if status:
            self.com_is_open = True
            self.open_thread_receive_and_send()
            print(
                "✅ Update COM thành công"
            )
            return True
        print(
            "❌ Update COM thất bại"
        )
        self.com_is_open = False
        return False


    def send_data(
        self,
        data
    ):
        try:
            self.tx_queue.put_nowait(
                data
            )
            print(
                f"[TX Queue] ➜ {data}"
            )
        except queue.Full:
            print(
                "⚠️ TX Queue đầy"
            )


    def receive_data(self):
        data = (
            self.serial_com
            .receive_data()
        )
        if not data:
            return
        try:
            self.rx_queue.put_nowait(
                data
            )
        except queue.Full:
            print(
                "⚠️ RX Queue đầy"
            )
            try:
                self.rx_queue.get_nowait()
            except queue.Empty:
                pass


    def _listen_serial(self):
        print("✅ Mở luồng RX")
        while self.running_rx:
            try:
                self.receive_data()
                time.sleep(0.001)
            except Exception as e:
                print(
                    "[RX Thread] Lỗi:",
                    e
                )
                time.sleep(1)


    def _send_serial(self):
        print("✅ Mở luồng TX")
        while self.running_tx:
            try:
                data = self.tx_queue.get(
                    timeout = 0.1
                )
                self.serial_com.send_data(
                    data
                )
            except queue.Empty:
                continue
            except Exception as e:
                print(
                    "[TX Thread] Lỗi:",
                    e
                )
                time.sleep(1)


    def get_data_from_queue(self):

        if self.rx_queue.empty():

            return None

        return self.rx_queue.get()


    def clear_tx_queue(self):

        with self.tx_queue.mutex:
            size = len(
                self.tx_queue.queue
            )
            self.tx_queue.queue.clear()
            self.tx_queue.unfinished_tasks = 0
        print(
            f"🗑️ Clear TX Queue: {size}"
        )


    def clear_rx_queue(self):
        with self.rx_queue.mutex:
            size = len(
                self.rx_queue.queue
            )
            self.rx_queue.queue.clear()
            self.rx_queue.unfinished_tasks = 0
        print(
            f"🗑️ Clear RX Queue: {size}"
        )


    def get_rx_queue_size(self):
        return self.rx_queue.qsize()


    def get_tx_queue_size(self):
        return self.tx_queue.qsize()

  
  
    def stop(self):
        print("🛑 Stop ManagerSerial")
        self.running_check = False
        self.close_thread_receive_and_send()
        self.serial_com.close_port()

    def is_running(self):
        return (
            self.com_is_open
            and self.rx_thread
            and self.rx_thread.is_alive()
            and self.tx_thread
            and self.tx_thread.is_alive()
        )