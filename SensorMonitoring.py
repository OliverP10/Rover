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


class SensorMonitoring:
    logger = logging.getLogger(__name__)

    serial_port: Serial
    enabled: bool = False


    def __init__(self, rover) -> None:
        self.rover = rover

    def setup(self):
        pass

    def set_enabled(self, enabled: int):
        self.enabled = bool(enabled)
        self.rover.communication.send_telemetry({"47": int(enabled)})
        self.logger.info("STOMP Enabled" if self.enabled else "STOMP Disabled")

    def check_sensors_data(self, sensor_data: dict):
        if not self.enabled: return
        for key, value in sensor_data.items():

            if "2" == key and 1 < value < 100:
                self.disarm_rover(key)
            elif "2" == key and 1 < value < 100:
                self.disarm_rover(key)

    def disarm_rover(self, key: str):
        self.logger.warn("STOMP event triggerd on sensor '"+key+"', disarming rover")
        self.rover.communication.send_telemetry({"46": int(key)})
        self.rover.arm.set_enabled(False)
        self.rover.movement.set_enabled(False)




            

                
                    
                    





