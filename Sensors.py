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
from SensorMonitoring import SensorMonitoring


class Sensors:
    logger = logging.getLogger(__name__)

    serial_port: Serial
    running: bool = False
    thread: Thread
    parse_fail_timer: int = time.time()
    parse_fail_count: int = 0
    sensor_monitoring: SensorMonitoring

    def __init__(self, rover) -> None:
        self.rover = rover
        self.sensor_monitoring = SensorMonitoring(self.rover)

    def setup(self):
        self.open_serial_port()
        self.thread: Thread = Thread(target=self.radio_read,args=())
        self.thread.start()

    def open_serial_port(self):
        try:
            self.serial_port = Serial('/dev/ttyACM0',57600,timeout=1)
            self.running = True
            self.logger.info("Sensor COM port opened")
        except Exception as e:
            self.logger.error('Sensor COM port error', exc_info=e)

    def reset_serial_port(self):
        self.serial_port.close()
        time.sleep(random.uniform(2,3))
        self.open_serial_port()


    def radio_read(self):
        while self.running:
            if(self.serial_port.in_waiting > 3):
                sensor_data: json = None
                try:
                    jsonString: str = self.serial_port.readline().decode().rstrip()
                    sensor_data = json.loads(jsonString)
                    self.sensor_monitoring.check_sensors_data(sensor_data)
                    self.rover.communication.send_telemetry(sensor_data)
                except Exception as e:
                    self.logger.error('Unable to decode sensor data')
                    self.parse_fail_count += 1
                    self.parse_fail_timer = time.time()

                if(self.parse_fail_count > 10):
                    self.logger.warn("Sensor parseing failure exceeded max count, resetting serial port")
                    self.parse_fail_count = 0
                    self.reset_serial_port()

                if(self.parse_fail_timer + 1000 < time.time()):
                    self.parse_fail_timer = time.time()
                    self.parse_fail_count = 0
            

                
                    
                    





