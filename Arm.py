from xmlrpc.client import Boolean
from Servo import Servo
from Claw import Claw
import logging
from time import sleep
from threading import Thread
import threading
from enum import Enum

class ARM_SEQUENCE(Enum):
    STOW = 0
    DEPLOY = 1
    LEFT_GRAB = 2
    RIGHT_GRAB = 3

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
        self.yaw = Servo(rover, "yaw", 62, 4, 140, 220)
        self.pitch1 = Servo(rover, "pitch1", 63, 5, 10, 140)
        self.pitch2 = Servo(rover, "pitch2", 64, 6, 24, 160)
        self.roll = Servo(rover, "roll", 65, 7, 7, 180)
        self.claw = Claw(rover, "claw", 67, 8, 19, 55)
        self.hatch = Servo(rover, "hatch", 69, 9, 0, 180)
        self.manual_override = False
        self.lock = threading.Lock()

    def setup(self):
        self.set_start_position()
        # self.set_enabled(False)
        self.load_sequence_mappings()

    def load_sequence_mappings(self) -> None:
        self.sequence_mappings[ARM_SEQUENCE.DEPLOY] = self.deploy_arm_sequence
        self.sequence_mappings[ARM_SEQUENCE.STOW] = self.stow_arm_sequence
        self.sequence_mappings[ARM_SEQUENCE.LEFT_GRAB] = self.left_grab_arm_sequence
        self.sequence_mappings[ARM_SEQUENCE.RIGHT_GRAB] = self.right_grab_arm_sequence


    def set_enabled(self, enabled: bool) -> None:
        self.yaw.set_enabled(enabled)
        self.pitch1.set_enabled(enabled)
        self.pitch2.set_enabled(enabled)
        self.roll.set_enabled(enabled)
        self.claw.set_enabled(enabled)
        self.hatch.set_enabled(enabled)
        self.logger.info("Arm Enabled" if enabled else "Arm Disabled")
        self.enabled = enabled
        self.rover.communication.send_telemetry({"70": int(self.enabled)})

    def set_manual_override(self, enabled: bool):
        self.yaw.set_permanent_override(enabled)
        self.pitch1.set_permanent_override(enabled)
        self.pitch2.set_permanent_override(enabled)
        self.roll.set_permanent_override(enabled)
        self.claw.servo.set_permanent_override(enabled)
        self.hatch.set_permanent_override(enabled)
        self.manual_override = enabled
        self.logger.warning("Manual override enabled" if enabled else "Manual override disabled")
        self.rover.communication.send_telemetry({"71": int(self.manual_override)})

    def set_start_position(self):
        self.set_enabled(True)
        self.yaw.set_angle(190, temp_override=True)
        self.pitch1.set_angle(4, temp_override=True)
        self.pitch2.set_angle(17, temp_override=True)
        self.roll.set_angle(101, temp_override=True)
        self.claw.servo.set_angle(20, temp_override=True)
        self.hatch.set_angle(0, temp_override=True)
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
        if self.manual_override:
            return True

        if ((self.current_sequence == ARM_SEQUENCE.STOW) and sequence_type == ARM_SEQUENCE.DEPLOY):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.DEPLOY) and sequence_type == ARM_SEQUENCE.LEFT_GRAB):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.DEPLOY) and sequence_type == ARM_SEQUENCE.RIGHT_GRAB):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.LEFT_GRAB) and sequence_type == ARM_SEQUENCE.DEPLOY):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.RIGHT_GRAB) and sequence_type == ARM_SEQUENCE.DEPLOY):
            return True
        elif ((self.current_sequence == ARM_SEQUENCE.DEPLOY) and sequence_type == ARM_SEQUENCE.STOW):
            return True
        else:
            self.logger.error("Cannot execute sequence '"+str(ARM_SEQUENCE(sequence_type)) +
                              "' while while arm is '"+str(ARM_SEQUENCE(self.current_sequence))+"'")
            return False

    def stow_arm_sequence(self):
        if (self.arm_sequence_checks(ARM_SEQUENCE.STOW)):
            self.logger.info("Executing sequence: "+str(ARM_SEQUENCE.STOW))
            self.next_sequence = str(ARM_SEQUENCE.STOW)
            self.rover.communication.send_telemetry({"73": int(ARM_SEQUENCE.STOW)})
            self.yaw.set_angle_with_delay(190, 1, 0.1)
            self.pitch1.set_angle_with_delay(4, 1, 0.1)
            self.pitch2.set_angle_with_delay(17, 1, 0.1)
            self.roll.set_angle_with_delay(101, 1, 0.1)
            self.claw.servo.set_angle_with_delay(20, 1, 0.1)
            
            self.current_sequence = ARM_SEQUENCE.STOW
            self.rover.communication.send_telemetry({"72": int(ARM_SEQUENCE.STOW)})
            self.logger.info("Finished executing sequence: "+str(ARM_SEQUENCE.STOW))
        self.lock.release()

    def deploy_arm_sequence(self):
        if (self.arm_sequence_checks(ARM_SEQUENCE.DEPLOY)):
            self.logger.info("Executing sequence: "+str(ARM_SEQUENCE.DEPLOY))
            self.next_sequence = str(ARM_SEQUENCE.DEPLOY)
            self.rover.communication.send_telemetry({"73": int(ARM_SEQUENCE.DEPLOY)})
            self.yaw.set_angle_with_delay(190, 1, 0.1)
            self.pitch2.set_angle_with_delay(20, 1, 0.1)
            self.pitch1.set_angle_with_delay(36, 1, 0.1)
            self.pitch2.set_angle_with_delay(25, 1, 0.1)
            self.roll.set_angle_with_delay(101, 1, 0.1)
            self.claw.servo.set_angle_with_delay(20, 1, 0.1)
            
            self.current_sequence = ARM_SEQUENCE.DEPLOY
            self.rover.communication.send_telemetry({"72": int(ARM_SEQUENCE.DEPLOY)})
            self.logger.info("Finished executing sequence: "+str(ARM_SEQUENCE.DEPLOY))
        self.lock.release()

    def left_grab_arm_sequence(self):
        pass
    
    def right_grab_arm_sequence(self):
        pass

    def checks(self) -> bool:
        if self.rover.arm.current_sequence.value != 1 and (not self.manual_override) :
            self.logger.warn("Can not move servo unless arm is deployed, current state: "+str(self.rover.arm.current_sequence))
            return False
        return True

    def set_yaw(self, angle: int):
        if self.checks():
            self.yaw.set_angle(angle)

    def set_pitch1(self, angle: int):
        if self.checks():
            self.pitch1.set_angle(angle)

    def set_pitch2(self, angle: int):
        if self.checks():
            self.pitch2.set_angle(angle)

    def set_roll(self, angle: int):
        if self.checks():
            self.roll.set_angle(angle)

    def set_claw(self, angle: int):
        if self.checks():
            self.claw.servo.set_angle(angle)

    def set_hatch(self, angle: int):
        self.hatch.set_angle(angle)

    def set_yaw(self, angle: int):
        if self.checks():
            self.yaw.set_angle(angle)

    def set_pitch1(self, angle: int):
        if self.checks():
            self.pitch1.set_angle(angle)

    def set_pitch2(self, angle: int):
        if self.checks():
            self.pitch2.set_angle(angle)

    def set_roll(self, angle: int):
        if self.checks():
            self.roll.set_angle(angle)

    def set_claw(self, angle: int):
        if self.checks():
            self.claw.servo.set_angle(angle)

    def set_hatch(self, angle: int):
        self.hatch.set_angle(angle)
    
    def yaw_turn_clockwise(self):
        if self.checks():
            self.yaw.turn_clockwise()

    def yaw_turn_counter_clockwise(self):
        if self.checks():
            self.yaw.turn_counter_clockwise()

    def pitch1_turn_clockwise(self):
        if self.checks():
            self.pitch1.turn_clockwise()

    def pitch1_turn_counter_clockwise(self):
        if self.checks():
            self.pitch1.turn_counter_clockwise()

    def pitch2_turn_clockwise(self):
        if self.checks():
            self.pitch2.turn_clockwise()

    def pitch2_turn_counter_clockwise(self):
        if self.checks():
            self.pitch2.turn_counter_clockwise()

    def roll_turn_clockwise(self):
        if self.checks():
            self.roll.turn_clockwise()

    def roll_turn_counter_clockwise(self):
        if self.checks():
            self.roll.turn_counter_clockwise()

    def claw_open(self):
        if self.checks():
            self.claw.open()

    def claw_close(self):
        if self.checks():
            self.claw.close()

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
        self.hatch.send_all_telem()

        # connect everything, arm the arm restart server and refresh page and the arm turns green
