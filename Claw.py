import logging
from Motor import Motor

class Claw:
    logger: any
    rover: any
    motor: Motor
    speed: int

    def __init__(self, rover, input_one:int, input_two:int, pwm_pin:int) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.enabled = False
        self.speed = 1
        self.motor = Motor(rover, "claw_motor", input_one, input_two, pwm_pin, False)

    def set_enabled(self, enabled:bool):
        self.motor.enable() if enabled else self.motor.disable()
        self.enabled = enabled
        self.logger.info("Armed" if enabled else "Disarmed")
        self.rover.communication.send_telemetry({"claw_enabled": enabled})

    def open(self):
        if self.checks():
            self.motor.set_backward()
            self.motor.set_speed(self.speed)
            self.rover.communication.send_telemetry({"claw_status": "opening"})

    def stop(self):
        self.motor.set_speed(0, override=True)
        self.rover.communication.send_telemetry({"claw_status": "neutral"})

    def close(self):
        if self.checks():
            self.motor.set_forward()
            self.motor.set_speed(self.speed)
            self.rover.communication.send_telemetry({"claw_status": "closeing"})

    def checks(self):
        if self.enabled:
            return True
        else:
            self.logger.error("Cannot move claw while disabled")
            return False

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"claw_enabled": self.enabled})

    

