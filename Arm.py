from Servo import Servo
import logging

class Arm:
    logger: any
    rover: any
    yaw: Servo
    pitch1: Servo 
    pitch2: Servo
    claw: Servo
    enabled: bool

    def __init__(self, rover) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.yaw = Servo(rover, "yaw", 0, 0, 180)
        self.pitch1 = Servo(rover, "pitch1", 1, 0, 180)
        self.pitch2 = Servo(rover, "pitch2", 2, 0, 180)
        self.claw = Servo(rover, "claw", 3, 0, 180)
        self.set_start_position()
        self.set_enabled(False)

    def set_enabled(self, boolean: bool) -> None:
        self.yaw.set_enabled(boolean)
        self.pitch1.set_enabled(boolean)
        self.pitch2.set_enabled(boolean)
        self.claw.set_enabled(boolean)
        self.logger.info("Arm Enabled" if boolean else "Arm Disabled")
        self.enabled = boolean
        self.rover.communication.send_telemetry({"arm_enabled":boolean})

    def set_start_position(self):
        self.set_enabled(True)
        self.yaw.set_angle(0)
        self.pitch1.set_angle(0)
        self.pitch2.set_angle(0)
        self.claw.set_angle(0)
        self.logger.info("Arm set to default position")

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"arm_enabled":self.enabled})
        self.yaw.send_all_telem()
        self.pitch1.send_all_telem()
        self.pitch2.send_all_telem()
        self.claw.send_all_telem()

        #connect everything, arm the arm restart server and refresh page and the arm turns green