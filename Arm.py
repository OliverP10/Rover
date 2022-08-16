from xmlrpc.client import Boolean
from Servo import Servo
from Claw import Claw
from Motor import Motor
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
    claw: Claw
    enabled: bool
    manual_override:bool
    current_sequence: str
    sequence_mappings: dict

    def __init__(self, rover) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.sequence_mappings = dict()
        self.current_sequence = "stowed"
        self.yaw = Servo(rover, "yaw", 0, 120, 136)
        self.pitch1 = Servo(rover, "pitch1", 1, 10, 130)
        self.pitch2 = Servo(rover, "pitch2", 2, 0, 180)
        self.claw = Claw(rover, 26, 9, 3)
        self.manual_override=False
        self.lock = threading.Lock()
       

        self.set_start_position()
        self.set_enabled(False)
        self.load_sequence_mappings()

    def load_sequence_mappings(self) -> None:
        self.sequence_mappings["arm_unstow"] = self.unstow_arm_sequence
        self.sequence_mappings["arm_deploy"] = self.deploy_arm_sequence
        self.sequence_mappings["arm_store"] = self.store_arm_sequence

    def set_enabled(self, enabled: bool) -> None:
        self.yaw.set_enabled(enabled)
        self.pitch1.set_enabled(enabled)
        self.pitch2.set_enabled(enabled)
        self.claw.set_enabled(enabled)
        self.logger.info("Arm Enabled" if enabled else "Arm Disabled")
        self.enabled = enabled
        self.rover.communication.send_telemetry({"arm_enabled":enabled})

    def set_manual_override(self, enabled:bool):
        self.yaw.set_permanent_override(enabled)
        self.pitch1.set_permanent_override(enabled)
        self.pitch2.set_permanent_override(enabled)
        self.manual_override = enabled
        self.logger.warning("Manual override enabled" if enabled else "Manual override disabled")
        self.rover.communication.send_telemetry({"arm_manual_override":enabled})

    def set_start_position(self):
        self.set_enabled(True)
        self.yaw.set_angle(17,temp_override=True)
        self.pitch1.set_angle(30,temp_override=True)
        self.pitch2.set_angle(150,temp_override=True)
        self.logger.info("Arm set to default position")

    def execute_sequence(self, sequence_name:str) -> None:
        if(self.lock.acquire(blocking=False)):
            thread = Thread(target = self.sequence_mappings[sequence_name], args = ())
            thread.start()
        else:
            self.logger.error("Can not execute multiple sequences at a given time")

    def arm_sequence_checks(self,sequence_type:str):
        if not self.enabled:
            self.logger.error("Cannot execute sequence '"+sequence_type+" arm' while it is disarmed")
            return False

        if ((self.current_sequence == "stowed") and sequence_type == "unstow"):
            return True
        elif ((self.current_sequence == "deployed") and sequence_type == "store"):
            return True
        elif ((self.current_sequence == "store") and sequence_type == "deploy"):
            return True
        else:
            self.logger.error("Cannot execute sequence '"+sequence_type+"' while while arm is '"+self.current_sequence+"'")
            return False

    def unstow_arm_sequence(self):
        if(self.arm_sequence_checks("unstow")):
            self.yaw.set_angle(17, temp_override=True)
            self.pitch1.set_angle(30, temp_override=True)
            self.pitch1.set_angle_with_delay(120,1,0.1)
            self.yaw.set_angle_with_delay(130,1,0.1)
            self.pitch1.set_angle_with_delay(60,1,0.1)
            self.current_sequence = "deployed"
        self.lock.release()

    def store_arm_sequence(self):
        if(self.arm_sequence_checks("store")):
            self.pitch1.set_angle_with_delay(120,1,0.1)
            self.yaw.set_angle_with_delay(17,1,0.1)
            self.pitch1.set_angle_with_delay(100,1,0.1)
            self.current_sequence = "store"
        self.lock.release()

    def deploy_arm_sequence(self):
        if(self.arm_sequence_checks("deploy")):
            self.pitch1.set_angle_with_delay(120,1,0.1)
            self.yaw.set_angle_with_delay(130,1,0.1)
            self.pitch1.set_angle_with_delay(60,1,0.1)
            self.current_sequence = "deployed"
        self.lock.release()

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"arm_enabled":self.enabled})
        self.rover.communication.send_telemetry({"arm_manual_override":self.manual_override})
        self.yaw.send_all_telem()
        self.pitch1.send_all_telem()
        self.pitch2.send_all_telem()
        self.claw.send_all_telem()

        #connect everything, arm the arm restart server and refresh page and the arm turns green