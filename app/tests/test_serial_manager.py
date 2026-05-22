
import time
from queue import Queue

from app.repository import (
    ComRepository
)

from app.manager.serial.serial_connect import (
    SerialConnect
)

from app.manager.serial.serial_manager import (
    ManagerSerial
)

from app.config import (
    PATH_FILE_DATA_CONFIG_COM
)

# ==========================================================
# CREATE OBJECT
# ==========================================================

repo = ComRepository(
    PATH_FILE_DATA_CONFIG_COM
)

serial_connect = SerialConnect(
    repo
)

serial_manager = ManagerSerial(
    serial_com=serial_connect,
    queue_rx=Queue(),
    queue_tx=Queue()
)



def test_update_com():

    print("\n===== TEST UPDATE COM =====")

    status = serial_manager.update_com(
        "COM2",
        115200
    )

    print(
        "Update COM:",
        status
    )

# ==========================================================
# TEST SEND DATA
# ==========================================================

def test_send_data():
    print("\n===== TEST SEND DATA =====")
    serial_manager.send_data(
        "VuVinhAnh"
    )
    time.sleep(1)

# ==========================================================
# TEST RECEIVE DATA
# ==========================================================

def test_receive_data():

    print("\n===== TEST RECEIVE DATA =====")

    timeout = 10
    start = time.time()

    while True:

        data = (
            serial_manager
            .get_data_from_queue()
        )

        if data:

            print(
                "Receive:",
                data
            )

            break

        if time.time() - start > timeout:

            print(
                "❌ Timeout receive"
            )

            break

        time.sleep(0.1)

# ==========================================================
# TEST RX QUEUE SIZE
# ==========================================================

def test_rx_queue_size():

    print("\n===== TEST RX QUEUE SIZE =====")

    size = (
        serial_manager
        .get_rx_queue_size()
    )

    print(
        "RX Queue Size:",
        size
    )

# ==========================================================
# TEST TX QUEUE SIZE
# ==========================================================

def test_tx_queue_size():

    print("\n===== TEST TX QUEUE SIZE =====")

    size = (
        serial_manager
        .get_tx_queue_size()
    )

    print(
        "TX Queue Size:",
        size
    )

# ==========================================================
# TEST CLEAR RX QUEUE
# ==========================================================

def test_clear_rx_queue():

    print("\n===== TEST CLEAR RX QUEUE =====")

    serial_manager.clear_rx_queue()

# ==========================================================
# TEST CLEAR TX QUEUE
# ==========================================================

def test_clear_tx_queue():

    print("\n===== TEST CLEAR TX QUEUE =====")

    serial_manager.clear_tx_queue()

# ==========================================================
# TEST STOP MANAGER
# ==========================================================

def test_stop_manager():

    print("\n===== TEST STOP MANAGER =====")

    serial_manager.stop()

# ==========================================================
# TEST AUTO SEND
# ==========================================================

def test_auto_send():

    print("\n===== TEST AUTO SEND =====")

    count = 0

    while True:

        data = f"hello {count}"

        serial_manager.send_data(
            data
        )

        print(
            f"Send: {data}"
        )

        count += 1

        time.sleep(0.1)

# ==========================================================
# TEST AUTO RECEIVE
# ==========================================================

def test_auto_receive():

    print("\n===== TEST AUTO RECEIVE =====")

    while True:

        data = (
            serial_manager
            .get_data_from_queue()
        )

        if data:

            print(
                "Receive:",
                data
            )

        time.sleep(0.01)

# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    # test_update_com()

    # test_send_data()

    # test_receive_data()

    # test_rx_queue_size()

    # test_tx_queue_size()

    # test_clear_rx_queue()

    # test_clear_tx_queue()

    # test_auto_send()

    # test_auto_receive()

    # test_stop_manager()

    pass