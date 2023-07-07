from socketio import Client
from threading import Lock
import logging
import Common
import json
import time
from typing import List
from WifiCommunication import WifiCommunication
from RadioCommunication import RadioCommunication

class Communicaition:
    logger = logging.getLogger(__name__)
    connected: bool = False

    wifi_communication: WifiCommunication
    radio_communication: RadioCommunication

    def __init__(self, rover) -> None:
        self.rover = rover
        self.radio_communication = RadioCommunication(self.rover)
        self.wifi_communication = WifiCommunication(self.rover)

    def setup(self):
        self.wifi_communication.setup()
        self.radio_communication.setup()

    def check_connection_status(self):
        if self.wifi_communication.connected:
            self.connected = True
        elif self.radio_communication.connected:
            self.connected = True
        else:
            self.connected = False

    def send_telemetry(self, data: dict):
        self.radio_communication.send_telemetry(data)
        self.wifi_communication.send_telemetry(data)

    def send_log(self, log: str):
        self.wifi_communication.send_log(log)

    def send_all_rover_telem(self):
        self.rover.movement.send_all_telem()
        self.rover.arm.send_all_telem()
