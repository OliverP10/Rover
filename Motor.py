import logging
from turtle import speed
import RPi.GPIO as GPIO


class Motor:    #i think its using GPIo.BCM rather than board
    logger: any
    rover: any

    input_one_pin: int
    input_two_pin: int
    pwm_pin: int

    invert: bool
    name: str
    __enabled:bool
    forwards: bool
    speed: float
    
    def __init__(self, rover: any, name:str, input_one:int, input_two:int, pwm_pin:int, invert:bool) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.name = name
        self.input_one_pin = input_one
        self.input_two_pin = input_two
        self.pwm_pin = pwm_pin
        self.invert = invert
        self.__enabled = True
        self.forwards = True
        self.speed = 0
        self.setup()
        self.disable()
        
    def setup(self):
        GPIO.setup(self.input_one_pin, GPIO.OUT)
        GPIO.setup(self.input_two_pin, GPIO.OUT)

        
    def disable(self):
        self.__enabled = False
        GPIO.output(self.input_one_pin, GPIO.LOW)
        GPIO.output(self.input_two_pin, GPIO.LOW)
        self.set_speed(0,override=True)
        self.rover.communication.send_telemetry({self.name+"_enabled":False})

    def enable(self):
        self.__enabled = True
        self.set_forward()
        self.set_speed(0,override=True)
        self.rover.communication.send_telemetry({self.name+"_enabled":True})
        
    def set_forward(self):
        if(self.__enabled):
            directionA, directionB = (GPIO.LOW, GPIO.HIGH) if self.invert else (GPIO.HIGH, GPIO.LOW)
            GPIO.output(self.input_one_pin, directionA)
            GPIO.output(self.input_two_pin, directionB)
            self.rover.communication.send_telemetry({self.name+"_forwards":True})
            self.forwards = True

    def set_backward(self):  
        if(self.__enabled):
            directionA, directionB = (GPIO.LOW, GPIO.HIGH) if self.invert else (GPIO.HIGH, GPIO.LOW)
            GPIO.output(self.input_one_pin, directionB)
            GPIO.output(self.input_two_pin, directionA)
            self.rover.communication.send_telemetry({self.name+"_forwards":False})
            self.forwards = False

    def set_speed(self, speed:float, override:bool=False):
        if(self.__enabled or override):
            self.rover.pwm_controller.set_motor(self.pwm_pin, speed)
            self.speed = speed
            self.rover.communication.send_telemetry({self.name+"_speed":speed})


    def send_all_telem(self):
        self.rover.communication.send_telemetry({self.name+"_enabled":self.__enabled})
        self.rover.communication.send_telemetry({self.name+"_forwards":self.forwards})
        self.rover.communication.send_telemetry({self.name+"_speed":self.speed})
