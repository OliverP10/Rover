import logging
from turtle import speed
import RPi.GPIO as GPIO


class ClawMotor:  # i think its using GPIo.BCM rather than board
    logger: any
    rover: any

    input_one_pin: int
    input_two_pin: int
    pwm_pin: int

    invert: bool
    name: str
    telemetry_id: int
    enabled: bool
    forwards: bool
    speed: float

    def __init__(self, rover: any, name: str, telemetry_id: int, input_one: int, input_two: int, pwm_pin: int, invert: bool) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.name = name
        self.telemetry_id = telemetry_id
        self.input_one_pin = input_one
        self.input_two_pin = input_two
        self.pwm_pin = pwm_pin
        self.invert = invert
        self.enabled = True
        self.forwards = True
        self.speed = 0

        self.enabled_telemetry_offset = 0
        self.forwards_telemetry_offset = 1
        self.speed_telemetry_offset = 2

        self.setup()
        self.disable()

    def setup(self):
        GPIO.setup(self.input_one_pin, GPIO.OUT)
        GPIO.setup(self.input_two_pin, GPIO.OUT)

    def disable(self):
        self.enabled = False
        GPIO.output(self.input_one_pin, GPIO.LOW)
        GPIO.output(self.input_two_pin, GPIO.LOW)
        self.set_speed(0, override=True)
        self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(False)})

    def enable(self):
        self.enabled = True
        self.set_forward()
        self.set_speed(0, override=True)
        self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(True)})

    def set_forward(self):
        if (self.enabled):
            directionA, directionB = (GPIO.LOW, GPIO.HIGH) if self.invert else (GPIO.HIGH, GPIO.LOW)
            GPIO.output(self.input_one_pin, directionA)
            GPIO.output(self.input_two_pin, directionB)
            self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(True)})
            self.forwards = True

    def set_backward(self):
        if (self.enabled):
            directionA, directionB = (GPIO.LOW, GPIO.HIGH) if self.invert else (GPIO.HIGH, GPIO.LOW)
            GPIO.output(self.input_one_pin, directionB)
            GPIO.output(self.input_two_pin, directionA)
            self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(False)})
            self.forwards = False

    def set_speed(self, speed: float, override: bool = False):
        if (self.enabled or override):
            self.rover.pwm_controller.set_motor(self.pwm_pin, speed)
            self.speed = speed
            self.rover.communication.send_telemetry({self.telemetry_id+self.speed_telemetry_offset: speed})

    def send_all_telem(self):
        self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(self.enabled)})
        self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(self.forwards)})
        self.rover.communication.send_telemetry({self.telemetry_id+self.speed_telemetry_offset: int(self.speed)})
