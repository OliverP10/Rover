from xmlrpc.client import Boolean
from Servo import Servo
from Claw import Claw
from Motor import Motor
from ClawMotor import ClawMotor
import logging
from time import sleep
from threading import Thread
import threading
from enum import Enum

class ARM_SEQUENCE(Enum):
    STORE = 0
    DEPLOY = 1
    STOW = 2

    def __str__(self):
        return '%s' % self.name
    
    def __int__(self):
        return self.value

class Arm:
    logger: any
    rover: any
    yaw: Servo
    pitch1: Servo
    pitch2: Servo
    roll: Servo
    claw: Claw
    enabled: bool
    manual_override: bool
    current_sequence: ARM_SEQUENCE
    next_sequence: ARM_SEQUENCE
    sequence_mappings: dict

    def __init__(self, rover) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.sequence_mappings = dict()
        self.current_sequence = ARM_SEQUENCE.STOW
        self.next_sequence = ARM_SEQUENCE.STOW
        self.yaw = Servo(rover, "yaw", 62, 0, 120, 136)
        self.pitch1 = Servo(rover, "pitch1", 63, 1, 10, 130)
        self.pitch2 = Servo(rover, "pitch2", 64, 2, 0, 180)
        self.roll = Servo(rover, "roll", 65, 3, 0, 180)
        self.claw = Claw(rover, 5, 6, 4)
        self.manual_override = False
        self.lock = threading.Lock()

        self.set_start_position()
        self.set_enabled(False)
        self.load_sequence_mappings()

    def load_sequence_mappings(self) -> None:
        self.sequence_mappings[ARM_SEQUENCE.STORE] = self.store_arm_sequence
        self.sequence_mappings[ARM_SEQUENCE.DEPLOY] = self.deploy_arm_sequence
        self.sequence_mappings[ARM_SEQUENCE.STOW] = self.stow_arm_sequence

    def set_enabled(self, enabled: bool) -> None:
        self.yaw.set_enabled(enabled)
        self.pitch1.set_enabled(enabled)
        self.pitch2.set_enabled(enabled)
        self.roll.set_enabled(enabled)
        self.claw.set_enabled(enabled)
        self.logger.info("Arm Enabled" if enabled else "Arm Disabled")
        self.enabled = enabled
        self.rover.communication.send_telemetry({"70": int(self.enabled)})

    def set_manual_override(self, enabled: bool):
        self.yaw.set_permanent_override(enabled)
        self.pitch1.set_permanent_override(enabled)
        self.pitch2.set_permanent_override(enabled)
        self.roll.set_permanent_override(enabled)
        self.manual_override = enabled
        self.logger.warning("Manual override enabled" if enabled else "Manual override disabled")
        self.rover.communication.send_telemetry({"71": int(self.manual_override)})

    def set_start_position(self):
        self.set_enabled(True)
        self.yaw.set_angle(17, temp_override=True)
        self.pitch1.set_angle(30, temp_override=True)
        self.pitch2.set_angle(150, temp_override=True)
        self.roll.set_angle(150, temp_override=True)
        self.logger.info("Arm set to default position")

    def execute_sequence(self, sequence_number: int) -> None:
        if ARM_SEQUENCE(sequence_number) not in self.sequence_mappings:
            self.logger.error("Can not execute sequences "+str(ARM_SEQUENCE(sequence_number))+", does't exist")
            return
        if (self.lock.acquire(blocking=False)):
            thread = Thread(target=self.sequence_mappings[ARM_SEQUENCE(sequence_number)], args=())
            thread.start()
        else:
            self.logger.error("Can not execute multiple sequences at a given time")

    def arm_sequence_checks(self, sequence_type: ARM_SEQUENCE):
        if not self.enabled:
            self.logger.error("Cannot execute sequence '"+str(ARM_SEQUENCE(sequence_type))+"' while arm is disarmed")
            return False

        if ((self.current_sequence == ARM_SEQUENCE.STOW) and sequence_type == ARM_SEQUENCE.STORE):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.STORE) and sequence_type == ARM_SEQUENCE.DEPLOY):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.DEPLOY) and sequence_type == ARM_SEQUENCE.STORE):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.STORE) and sequence_type == ARM_SEQUENCE.STOW):
            return True
        else:
            self.logger.error("Cannot execute sequence '"+str(ARM_SEQUENCE(sequence_type)) +
                              "' while while arm is '"+str(ARM_SEQUENCE(self.current_sequence))+"'")
            return False

    def store_arm_sequence(self):
        if (self.arm_sequence_checks(ARM_SEQUENCE.STORE)):
            self.logger.info("Executing sequence: "+str(ARM_SEQUENCE.STORE))
            self.next_sequence = str(ARM_SEQUENCE.STORE)
            self.rover.communication.send_telemetry({"73": int(ARM_SEQUENCE.STORE)})
            self.yaw.set_angle(17, temp_override=True)
            self.pitch1.set_angle(30, temp_override=True)
            self.pitch1.set_angle_with_delay(120, 1, 0.1)
            self.yaw.set_angle_with_delay(130, 1, 0.1)
            self.pitch1.set_angle_with_delay(60, 1, 0.1)
            self.current_sequence = ARM_SEQUENCE.STORE
            self.rover.communication.send_telemetry({"72": int(ARM_SEQUENCE.STORE)})
            self.logger.info("Finished executing sequence: "+str(ARM_SEQUENCE.STORE))
        self.lock.release()

    def deploy_arm_sequence(self):
        if (self.arm_sequence_checks(ARM_SEQUENCE.DEPLOY)):
            self.logger.info("Executing sequence: "+str(ARM_SEQUENCE.DEPLOY))
            self.next_sequence = str(ARM_SEQUENCE.DEPLOY)
            self.rover.communication.send_telemetry({"73": int(ARM_SEQUENCE.DEPLOY)})
            self.pitch1.set_angle_with_delay(120, 1, 0.1)
            self.yaw.set_angle_with_delay(17, 1, 0.1)
            self.pitch1.set_angle_with_delay(100, 1, 0.1)
            self.current_sequence = ARM_SEQUENCE.DEPLOY
            self.rover.communication.send_telemetry({"72": int(ARM_SEQUENCE.DEPLOY)})
            self.logger.info("Finished executing sequence: "+str(ARM_SEQUENCE.DEPLOY))
        self.lock.release()

    def stow_arm_sequence(self):
        if (self.arm_sequence_checks(ARM_SEQUENCE.STOW)):
            self.logger.info("Executing sequence: "+str(ARM_SEQUENCE.STOW))
            self.next_sequence = str(ARM_SEQUENCE.STOW)
            self.rover.communication.send_telemetry({"73": int(ARM_SEQUENCE.STOW)})
            self.yaw.set_angle(17, temp_override=True)
            self.pitch1.set_angle(30, temp_override=True)
            self.pitch1.set_angle_with_delay(120, 1, 0.1)
            self.yaw.set_angle_with_delay(130, 1, 0.1)
            self.pitch1.set_angle_with_delay(60, 1, 0.1)
            self.current_sequence = ARM_SEQUENCE.STOW
            self.rover.communication.send_telemetry({"72": int(ARM_SEQUENCE.STOW)})
            self.logger.info("Finished executing sequence: "+str(ARM_SEQUENCE.STOW))
        self.lock.release()

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"70": int(self.enabled)})
        self.rover.communication.send_telemetry({"71": int(self.manual_override)})
        self.rover.communication.send_telemetry({"72": int(self.current_sequence)})
        self.rover.communication.send_telemetry({"73": int(self.current_sequence)})
        self.yaw.send_all_telem()
        self.pitch1.send_all_telem()
        self.pitch2.send_all_telem()
        self.roll.send_all_telem()
        self.claw.send_all_telem()

        # connect everything, arm the arm restart server and refresh page and the arm turns green
