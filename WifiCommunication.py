from socketio import Client
from threading import Lock
import logging
import Common
import json
import time
from typing import List



class WifiCommunication:
    logger = logging.getLogger(__name__)
    sio: Client = Client()
    lock: Lock = Lock()
    telemetry_buffer: any = []
    log_buffer: any = []
    connected: bool = False                     # Built in one doesnt work
    reconection: bool = False

    def __init__(self, rover) -> None:
        self.rover = rover

    def setup(self):
        self.call_backs()
        try:
            self.sio.connect('http://'+Common.ROOT_IP+':3000')
        except Exception as e:
            self.logger.critical("Unable to connect to server: ", exc_info=e)

    def call_backs(self) -> None:

        @self.sio.event
        def connect() -> None:
            self.connected = True
            self.logger.info("WiFi connected")
            self.sio.emit("setType", "vehicle")
            self.rover.communication.check_connection_status()

            if self.reconection:
                self.send_all_rover_telem()
                self.flush_buffer()


        @self.sio.event
        def disconnect() -> None:
            self.connected = False
            self.reconection = True
            self.logger.warn("WiFi disconnected")
            self.rover.communication.check_connection_status()

        @self.sio.on('control-frame')
        def control_frame(data: json) -> None:
            if (self.lock.acquire()):  # blocking=False
                self.rover.decode_control_frame(data)
                self.lock.release()
            else:
                self.logger.warn("Blocking concurrent control frame commands")

    def send_telemetry(self, data: dict):
        if (self.connected):
            self.sio.emit("telemetry", json.dumps(data))
        else:
            self.telemetry_buffer.append(data)

    def send_log(self, log: str):
        if (self.connected):
            self.sio.emit("log", log)
        else:
            self.log_buffer.append(log)

    def flush_buffer(self):
        try:
            for data in self.telemetry_buffer:
                self.sio.emit("telemetry", json.dumps(data))
            self.telemetry_buffer = []

            for log in self.log_buffer:
                self.sio.emit("log", log)
            self.log_buffer = []
            self.logger.info("Cleared bufferd items")
        except Exception as e:
            self.logger.error("Unable to clear buffer")


    def send_all_rover_telem(self):
        self.rover.movement.send_all_telem()
        self.rover.arm.send_all_telem()
