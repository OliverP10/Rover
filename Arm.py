from Servo import Servo
import logging
from time import sleep
from threading import Thread
import threading


class Arm:
    logger: any
    rover: any
    yaw: Servo
    pitch1: Servo 
    pitch2: Servo
    enabled: bool
    sequence_mappings: dict

    def __init__(self, rover) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.sequence_mappings = dict()
        self.yaw = Servo(rover, "yaw", 0, 0, 180)
        self.pitch1 = Servo(rover, "pitch1", 1, 0, 180)
        self.pitch2 = Servo(rover, "pitch2", 2, 0, 180)

        self.set_start_position()
        self.set_enabled(False)
        self.lock = threading.Lock()
        self.load_sequence_mappings()

    def load_sequence_mappings(self) -> None:
        self.sequence_mappings["arm_deploy"] = self.depoly_arm_sequence

    def set_enabled(self, boolean: bool) -> None:
        self.yaw.set_enabled(boolean)
        self.pitch1.set_enabled(boolean)
        self.pitch2.set_enabled(boolean)
        self.logger.info("Arm Enabled" if boolean else "Arm Disabled")
        self.enabled = boolean
        self.rover.communication.send_telemetry({"arm_enabled":boolean})

    def set_start_position(self):
        self.set_enabled(True)
        self.yaw.set_angle(0)
        self.pitch1.set_angle(0)
        self.pitch2.set_angle(0)
        self.logger.info("Arm set to default position")

    def execute_sequence(self, sequence_name:str) -> None:
        self.lock.acquire()
        thread = Thread(target = self.sequence_mappings[sequence_name], args = ())
        thread.start()


    def depoly_arm_sequence(self):
        if self.enabled:
            self.yaw.set_angle(0, override=True)
            self.pitch1.set_angle_with_delay(90,1,0.1)
        else:
            self.logger.error("Cannot deploy arm while it is disarmed")

        self.lock.release()

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"arm_enabled":self.enabled})
        self.yaw.send_all_telem()
        self.pitch1.send_all_telem()
        self.pitch2.send_all_telem()

        #connect everything, arm the arm restart server and refresh page and the arm turns green