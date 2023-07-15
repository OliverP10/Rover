from adafruit_servokit import ServoKit

class PwmController:
    kit: ServoKit

    def __init__(self) -> None:
        self.kit = ServoKit(channels=16)

        # kit.servo[0].actuation_range = 270
        # self.kit.servo[1].actuation_range = 250
        # kit.servo[2].actuation_range = 270
        # kit.servo[3].actuation_range = 270

        self.kit.servo[0].set_pulse_width_range(500, 2600)  # yaw
        self.kit.servo[1].set_pulse_width_range(500, 2600)  # pitch one
        self.kit.servo[2].set_pulse_width_range(500, 2600)  # pitch two
        self.kit.servo[3].set_pulse_width_range(500, 2600)  # roll
        self.kit.servo[3].set_pulse_width_range(500, 2600)  # roll

    def set_servo(self, servo_pin: int, angle: int):
        self.kit.servo[servo_pin].angle = angle

    # speed between 0 and 1
    def set_motor(self, motor_pin: int, speed: float):
        self.kit.continuous_servo[motor_pin].throttle = speed

    def set_no_pulse(self, pin: int):
        self.kit.servo[pin].angle = None
