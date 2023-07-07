from socketio import Client
from threading import Lock
import logging
import Common
import json
import time
from typing import List
from serial import Serial
from threading import Thread
import time
import random


class RadioCommunication:
    logger = logging.getLogger(__name__)

    serial_port: Serial
    running: bool = False
    thread: Thread
    connected: bool = False
    parse_fail_timer: int = time.time()
    parse_fail_count: int = 0

    def __init__(self, rover) -> None:
        self.rover = rover

    def setup(self):
        self.open_serial_port()
        self.thread: Thread = Thread(target=self.radio_read,args=())
        self.thread.start()

    def open_serial_port(self):
        try:
            self.serial_port = Serial('/dev/ttyUSB0',57600,timeout=1)
            self.running = True
        except Exception as e:
            self.logger.error('Radio COM port error', exc_info=e)

    def reset_serial_port(self):
        self.serial_port.close()
        time.sleep(random.uniform(2,3))
        self.open_serial_port()

    def setRadioConnected(self, connection: int):
        connection = bool(connection)
        self.connected = connection
        if connection:
            self.logger.info("Radio connected")
        else:
            self.logger.warn("Radio disconnected")
        self.rover.communication.check_connection_status()

    def send_telemetry(self, data: dict):
        if(self.running and self.serial_port.is_open):
            self.serial_port.write(str(json.dumps(data)).encode())

    def radio_read(self):
        while self.running:
            if(self.serial_port.in_waiting > 3):
                control_frame: json = None
                try:
                    jsonString: str = self.serial_port.readline().decode().rstrip()
                    control_frame = json.loads(jsonString)
                    self.rover.decode_control_frame(control_frame)
                except Exception as e:
                    self.logger.error('Unable to decode command data')
                    self.parse_fail_count += 1
                    self.parse_fail_timer = time.time()

                if(self.parse_fail_count > 10):
                    self.logger.warn("Radio parseing failure exceeded max count, resetting serial port")
                    self.parse_fail_count = 0
                    self.reset_serial_port()

                if(self.parse_fail_timer + 1000 < time.time()):
                    self.parse_fail_timer = time.time()
                    self.parse_fail_count = 0
            

                
                    
                    





