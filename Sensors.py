import logging
from logging import Logger
from serial import Serial
from threading import Thread
import json
import time

class Sensors:
    logger: any
    rover:any
    serialPort: Serial
    running: bool
    thread: Thread

    def __init__(self, rover) -> None:
        self.logger:Logger = logging.getLogger(__name__)
        self.rover = rover
        try:
            self.serialPort = Serial('/dev/ttyACM0',9600,timeout=1)
            self.rover.communication.send_arduino_status(True)
        except Exception as e:
            self.logger.error('COM port error', exc_info=e)
        self.running = True
        self.thread: Thread = Thread(target=self.run,args=())
        self.start()

    def start(self) -> None:
        self.thread.start()

    def run(self):
        while self.running:
            if(self.serialPort.is_open):
                line: bytes = self.serialPort.readline()
                if line:
                    try:
                        string: str = line.decode()
                        data: dict = json.loads(string)
                        self.rover.communication.send_telemetry(data)
                    except Exception as e:
                        self.logger.error('Unable to decode sensor data')
            else:
                self.rover.communication.send_arduino_status(False)
                time.sleep(0.5)

    def end(self) -> None:
        self.running = False