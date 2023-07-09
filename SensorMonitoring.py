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

            if "80" == key and value > 1:
                self.disarm_rover(key)
            elif "81" == key and value > 1:
                self.disarm_rover(key)
            elif "82" == key and value > 1:
                self.disarm_rover(key)
            elif "83" == key and value > 1:
                self.disarm_rover(key)
            elif "84" == key and value > 1:
                self.disarm_rover(key)
            elif "85" == key and value > 1:
                self.disarm_rover(key)
            elif "90" == key and value > 50:
                self.disarm_rover(key)
            elif "91" == key and value > 50:
                self.disarm_rover(key)
            elif "92" == key and value > 50:
                self.disarm_rover(key)
            elif "93" == key and value > 50:
                self.disarm_rover(key)
            elif "94" == key and value > 50:
                self.disarm_rover(key)
            elif "95" == key and value > 50:
                self.disarm_rover(key)
            elif "100" == key and value < 13.2:
                self.disarm_rover(key)
 

    def disarm_rover(self, key: str):
        self.logger.warn("STOMP event triggerd on sensor '"+key+"', disarming rover")
        self.rover.communication.send_telemetry({"46": int(key)})
        self.rover.arm.set_enabled(False)
        self.rover.movement.set_enabled(False)




            

                
                    
                    





