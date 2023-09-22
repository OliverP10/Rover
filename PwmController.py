from adafruit_servokit import ServoKit

class PwmController:
    kit: ServoKit

    def __init__(self) -> None:
        self.kit = ServoKit(channels=16)

        self.kit.servo[4].actuation_range = 270
        # self.kit.servo[1].actuation_range = 250
        # kit.servo[2].actuation_range = 270
        # kit.servo[3].actuation_range = 270

        self.kit.servo[0].set_pulse_width_range(500, 2500)  # wheel one
        self.kit.servo[1].set_pulse_width_range(500, 2500)  # wheel two
        self.kit.servo[2].set_pulse_width_range(500, 2500)  # wheel three
        self.kit.servo[3].set_pulse_width_range(500, 2500)  # wheel four

        self.kit.servo[4].set_pulse_width_range(500, 2500)  # yaw
        self.kit.servo[5].set_pulse_width_range(500, 2500)  # pitch one
        self.kit.servo[6].set_pulse_width_range(500, 2500)  # pitch two
        self.kit.servo[7].set_pulse_width_range(500, 2500)  # roll
        self.kit.servo[8].set_pulse_width_range(500, 2500)  # claw


    def set_servo(self, servo_pin: int, angle: int):
        self.kit.servo[servo_pin].angle = angle
        
    # speed between 0 and 1
    # def set_motor(self, motor_pin: int, speed: float):
    #     self.kit.continuous_servo[motor_pin].throttle = speed

    def set_no_pulse(self, pin: int):
        self.kit.servo[pin].angle = None
