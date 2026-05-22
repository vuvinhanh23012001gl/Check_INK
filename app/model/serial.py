# -*- coding: utf-8 -*-

import serial
class SerialConfig:
    def __init__(
        self,
        device_port=None,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
        reconnect_interval=1
    ):

        self.device_port = device_port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.reconnect_interval = reconnect_interval

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            device_port=data.get("device_port"),
            baudrate=data.get("baudrate", 115200),
            bytesize=data.get("bytesize", serial.EIGHTBITS),
            parity=data.get("parity", serial.PARITY_NONE),
            stopbits=data.get("stopbits", serial.STOPBITS_ONE),
            timeout=data.get("timeout", 1),
            reconnect_interval=data.get("reconnect_interval", 1)
        )

    def to_dict(self):
        return {
            "device_port": self.device_port,
            "baudrate": self.baudrate,
            "bytesize": self.bytesize,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "timeout": self.timeout,
            "reconnect_interval": self.reconnect_interval
        }

    def is_valid(self):
        return self.device_port is not None