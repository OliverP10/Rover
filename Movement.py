import logging
from Motor import Motor


class Movement:

    motor_one: Motor
    motor_two: Motor

    enabled: bool
    speed: float

    def __init__(self, rover) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.motor_one = Motor(rover, "motor_one", 50,  12, 6)
        self.motor_two = Motor(rover, "motor_two", 53,  18, 19)
        self.set_enabled(True)
        self.set_speed(0.5)

    def set_enabled(self, enabled: bool):
        self.motor_one.enable() if enabled else self.motor_one.disable()
        self.motor_two.enable() if enabled else self.motor_two.disable()
        self.enabled = enabled
        self.logger.info("Movment Enabled" if enabled else "Movment Disabled")
        self.rover.communication.send_telemetry({"48": int(enabled)})

    def set_speed(self, speed: float):
        self.speed = float(speed)
        self.rover.communication.send_telemetry({"49": speed})

    def left_forward(self):
        self.motor_one.set_forward()
        self.motor_one.set_speed(self.speed)

    def left_stop(self):
        self.motor_one.set_speed(0, override=True)

    def left_backward(self):
        self.motor_one.set_backward()
        self.motor_one.set_speed(self.speed)

    def right_forward(self):
        self.motor_two.set_forward()
        self.motor_two.set_speed(self.speed)

    def right_stop(self):
        self.motor_two.set_speed(0, override=True)

    def right_backward(self):
        self.motor_two.set_backward()
        self.motor_two.set_speed(self.speed)

    def all_forward(self):
        self.motor_one.set_forward()
        self.motor_two.set_forward()

        self.motor_one.set_speed(self.speed)
        self.motor_two.set_speed(self.speed)

    def all_stop(self):
        self.motor_one.set_speed(0, override=True)
        self.motor_two.set_speed(0, override=True)

        self.motor_one.set_forward()
        self.motor_two.set_forward()

    def all_backward(self):
        self.motor_one.set_backward()
        self.motor_two.set_backward()

        self.motor_one.set_speed(self.speed)
        self.motor_two.set_speed(self.speed)

    def send_all_telem(self):
        self.motor_one.send_all_telem()
        self.motor_two.send_all_telem()
