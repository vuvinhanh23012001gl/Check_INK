
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
        self._rx_subscribers = [self.rx_queue]
        self._connection_lock = threading.RLock()


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
        if self.running_rx and self.running_tx:
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




    def close_thread_receive_and_send(self, clear_tx=True):
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
        if clear_tx:
            self.clear_tx_queue()

    def stop(self):
        """Dừng luồng kiểm tra COM, RX/TX và đóng cổng serial."""
        self.running_check = False
        self.close_thread_receive_and_send()
        with self._connection_lock:
            self.serial_com.close_port()
        self.com_is_open = False



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
                with self._connection_lock:
                    port_exists = self.serial_com.check_port_exists(port_name)
                if not port_exists:
                    if self.com_is_open or (
                        self.serial_com.ser
                        and self.serial_com.ser.is_open
                    ):
                        print(
                            f"❌ Mất kết nối {port_name}"
                        )
                        self.com_is_open = False
                        self.serial_com.close_port()
                        self.close_thread_receive_and_send(clear_tx=False)
                    print("Cố gắng kết nối với COM ...")
                    time.sleep(5)
                    continue
                with self._connection_lock:
                    if self.serial_com.ser and not self.serial_com.ser.is_open:
                        self.serial_com.close_port()
                        self.com_is_open = False
                    needs_open = (
                        not self.serial_com.ser
                        or not self.serial_com.ser.is_open
                    )
                if needs_open:
                    print(
                        f"🔄 Đang mở {port_name}"
                    )
                    with self._connection_lock:
                        status = self.serial_com.open_port()
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
        with self._connection_lock:
            self.close_thread_receive_and_send()
            self.serial_com.close_port()
            status = self.serial_com.open_manual(port_name, baudrate)
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


    def subscribe_rx(self) -> Queue:
        """Tạo queue riêng cho một consumer nhận bản tin Serial.

        Input: không có.
        Output: queue chỉ được ``SerialRX`` ghi và consumer đó đọc.
        Errors: không phát sinh.
        """
        subscriber_queue = Queue()
        self._rx_subscribers.append(subscriber_queue)
        return subscriber_queue


    def receive_data(self):
        with self._connection_lock:
            data = self.serial_com.receive_data()
        if not data:
            return
        for subscriber_queue in tuple(self._rx_subscribers):
            try:
                subscriber_queue.put_nowait(data)
            except queue.Full:
                print("⚠️ RX Queue đầy")
                try:
                    subscriber_queue.get_nowait()
                    subscriber_queue.put_nowait(data)
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
                if not self.is_running():
                    time.sleep(0.05)
                    continue
                data = self.tx_queue.get(
                    timeout = 0.1
                )
                with self._connection_lock:
                    send_status = self.serial_com.send_data(data)
                if not send_status:
                    self.tx_queue.put_nowait(data)
                    self.com_is_open = False
                    self.running_tx = False
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
        total_size = 0
        for subscriber_queue in tuple(self._rx_subscribers):
            with subscriber_queue.mutex:
                size = len(subscriber_queue.queue)
                subscriber_queue.queue.clear()
                subscriber_queue.unfinished_tasks = 0
                total_size += size
        print(f"🗑️ Clear RX Queue: {total_size}")


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