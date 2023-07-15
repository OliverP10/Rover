import logging
import RPi.GPIO as GPIO


class Motor:
    logger: any
    rover: any

    pwm_pin_a: int
    pwm_pin_b: int
    pwm_a: any
    pwm_b: any

    name: str
    telemetry_id: int
    enabled: bool
    forwards: bool
    speed: float

    def __init__(self, rover: any, name: str, telemetry_id: int, pwm_pin_a: int, pwm_pin_b: int) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.name = name
        self.telemetry_id = telemetry_id
        self.pwm_pin_a = pwm_pin_a
        self.pwm_pin_b = pwm_pin_b
        self.enabled = True
        self.forwards = True
        self.speed = 0

        self.enabled_telemetry_offset = 0
        self.forwards_telemetry_offset = 1
        self.speed_telemetry_offset = 2

        self.setup()
        self.disable()

    def setup(self):
        GPIO.setup(self.pwm_pin_a, GPIO.OUT)
        GPIO.setup(self.pwm_pin_b, GPIO.OUT)
        self.pwm_a = GPIO.PWM(self.pwm_pin_a, 500)
        self.pwm_b = GPIO.PWM(self.pwm_pin_b, 500)
        self.pwm_a.start(0)
        self.pwm_b.start(0)

    def disable(self):
        self.enabled = False
        self.set_speed(0, override=True)
        self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(False)})

    def enable(self):
        self.enabled = True
        self.set_forward()
        self.set_speed(0, override=True)
        self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(True)})

    def set_forward(self):
        if (self.enabled):
            self.forwards = True
            self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(True)})

    def set_backward(self):
        if (self.enabled):
            self.forwards = False
            self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(False)})

    def set_speed(self, speed: float, override: bool = False):
        if (self.enabled or override):
            self.speed = speed
            
            if self.forwards:
                self.pwm_a.ChangeDutyCycle(self.speed*100)
                self.pwm_b.ChangeDutyCycle(0)
            else:
                self.pwm_a.ChangeDutyCycle(0)
                self.pwm_b.ChangeDutyCycle(self.speed*100)

            self.rover.communication.send_telemetry({self.telemetry_id+self.speed_telemetry_offset: speed})

    def send_all_telem(self):
        self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(self.enabled)})
        self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(self.forwards)})
        self.rover.communication.send_telemetry({self.telemetry_id+self.speed_telemetry_offset: int(self.speed)})



# import logging
# from turtle import speed
# import RPi.GPIO as GPIO


# class Motor:
#     logger: any
#     rover: any

#     direction_pin: int
#     pwm_pin: int

#     name: str
#     telemetry_id: int
#     enabled: bool
#     forwards: bool
#     speed: float

#     def __init__(self, rover: any, name: str, telemetry_id: int, direction_pin: int, pwm_pin: int) -> None:
#         self.logger = logging.getLogger(__name__)
#         self.rover = rover
#         self.name = name
#         self.telemetry_id = telemetry_id
#         self.direction_pin = direction_pin
#         self.pwm_pin = pwm_pin
#         self.enabled = True
#         self.forwards = True
#         self.speed = 0

#         self.enabled_telemetry_offset = 0
#         self.forwards_telemetry_offset = 1
#         self.speed_telemetry_offset = 2

#         self.setup()
#         self.disable()

#     def setup(self):
#         GPIO.setup(self.direction_pin, GPIO.OUT)

#     def disable(self):
#         self.enabled = False
#         self.set_speed(0, override=True)
#         self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(False)})

#     def enable(self):
#         self.enabled = True
#         self.set_forward()
#         self.set_speed(0, override=True)
#         self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(True)})

#     def set_forward(self):
#         if (self.enabled):
#             GPIO.output(self.direction_pin, GPIO.HIGH)
#             self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(True)})
#             self.forwards = True

#     def set_backward(self):
#         if (self.enabled):
#             GPIO.output(self.direction_pin, GPIO.LOW)
#             self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(False)})
#             self.forwards = False

#     def set_speed(self, speed: float, override: bool = False):
#         if (self.enabled or override):
#             GPIO.
#             self.rover.pwm_controller.set_motor(self.pwm_pin, speed)
#             self.speed = speed
#             self.rover.communication.send_telemetry({self.telemetry_id+self.speed_telemetry_offset: speed})

#     def send_all_telem(self):
#         self.rover.communication.send_telemetry({self.telemetry_id+self.enabled_telemetry_offset: int(self.enabled)})
#         self.rover.communication.send_telemetry({self.telemetry_id+self.forwards_telemetry_offset: int(self.forwards)})
#         self.rover.communication.send_telemetry({self.telemetry_id+self.speed_telemetry_offset: int(self.speed)})
