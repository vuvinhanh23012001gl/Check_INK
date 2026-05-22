# -*- coding: utf-8 -*-
import time
from app.repository import (
    ComRepository
)

from app.manager.serial.serial_connect import (
    SerialConnect
)

from app.model import (
    SerialConfig
)

from app.config import PATH_FILE_DATA_CONFIG_COM

# ==========================================================
# CREATE OBJECT
# ==========================================================

repo = ComRepository(
    PATH_FILE_DATA_CONFIG_COM
)


serial_manager = SerialConnect(
    repo
)


# ==========================================================
# TEST LIST PORTS
# ==========================================================

def test_list_ports():
    print("\n===== TEST LIST PORTS =====")
    ports = SerialConnect.list_ports()
    for port in ports:
        print(port)


# ==========================================================
# TEST SHOW PORT INFO
# ==========================================================

def test_show_port_info():
    print("\n===== TEST SHOW PORT INFO =====")
    SerialConnect.show_port_info()


# ==========================================================
# TEST CHECK PORT EXISTS
# ==========================================================

def test_check_port_exists():
    print("\n===== TEST CHECK PORT EXISTS =====")
    port_name = "COM3"
    status = SerialConnect.check_port_exists(
        port_name
    )
    print(
        f"Port {port_name} exists:",
        status
    )


# ==========================================================
# TEST CHECK PORT BUSY
# ==========================================================

def test_check_port_busy():
    print("\n===== TEST CHECK PORT BUSY =====")
    port_name = "COM2"

    busy = SerialConnect.is_port_busy(
        port_name
    )

    print(
        f"Port {port_name} busy:",
        busy
    )


# ==========================================================
# TEST LOAD CONFIG
# ==========================================================

def test_load_config():

    print("\n===== TEST LOAD CONFIG =====")

    print(
        serial_manager.config.to_dict()
    )


# ==========================================================
# TEST SAVE CONFIG
# ==========================================================

def test_save_config():

    print("\n===== TEST SAVE CONFIG =====")

    config = SerialConfig(

        device_port="COM3",

        baudrate=115200
    )

    serial_manager.update_config(
        config
    )

    print(
        "Save config success"
    )


# ==========================================================
# TEST OPEN PORT
# ==========================================================

def test_open_port():

    print("\n===== TEST OPEN PORT =====")

    status = serial_manager.open_port()

    print(
        "Open status:",
        status
    )


# ==========================================================
# TEST OPEN MANUAL
# ==========================================================

def test_open_manual():

    print("\n===== TEST OPEN MANUAL =====")

    status = serial_manager.open_manual(
        "COM3",
        115200
    )

    print(
        "Open manual:",
        status
    )


# ==========================================================
# TEST SEND DATA
# ==========================================================

def test_send_data():

    print("\n===== TEST SEND DATA =====")

    serial_manager.send_data(
        "hello stm32"
    )


# ==========================================================
# TEST RECEIVE DATA
# ==========================================================

def test_receive_data():

    print("\n===== TEST RECEIVE DATA =====")

    data = serial_manager.receive_data()

    print(
        "Receive:",
        data
    )


# ==========================================================
# TEST CLOSE PORT
# ==========================================================

def test_close_port():

    print("\n===== TEST CLOSE PORT =====")

    serial_manager.close_port()

    print(
        "Close success"
    )


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    # test_list_ports()

    # test_show_port_info()

    # test_check_port_exists()

    # test_check_port_busy()

    # test_load_config()

    # test_save_config()

    # test_open_manual()

    # test_send_data()

    # test_receive_data()

    # test_close_port()
    pass