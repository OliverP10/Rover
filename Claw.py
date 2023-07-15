import logging
from Servo import Servo


class Claw:
    logger: any
    rover: any
    servo: Servo
    speed: int

    def __init__(self, rover: any, name: str, telemetry_id: int, pin: int, min: int, max: int) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.enabled = False
        self.speed = 1
        self.servo = Servo(rover, "claw", telemetry_id, pin, min, max)

    def set_enabled(self, enabled: bool):
        self.servo.set_enabled(enabled)
        self.enabled = enabled
        self.logger.info("Armed" if enabled else "Disarmed")
        self.rover.communication.send_telemetry({66: int(self.enabled)})
        if not enabled: self.stop()

    def open(self):
        if self.checks():
            self.servo.turn_clockwise()
            self.rover.communication.send_telemetry({68: 0})

    def stop(self):
        self.servo.stop_turn()
        self.rover.communication.send_telemetry({68: 1})

    def close(self):
        if self.checks():
            self.servo.turn_counter_clockwise()
            self.rover.communication.send_telemetry({68: 2})

    def checks(self):
        if self.enabled:
            return True
        else:
            self.logger.error("Cannot move claw while disabled")
            return False

    def send_all_telem(self):
        self.rover.communication.send_telemetry({66: int(self.enabled)})
        self.servo.send_all_telem()
