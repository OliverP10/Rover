import logging
import time
import RPi.GPIO as GPIO

class Servo:
    logger: any
    rover: any
    name: str
    pin: int
    enabled: bool
    position: int
    update_rate: int

    last_triggered: int

    def __init__(self, rover:any, name:str, pin:int, min:int, max:int) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.name = name
        self.pin = pin
        self.min = min
        self.max = max
        self.enabled = False
        self.position = 0
        self.update_rate = 0.05
        self.last_triggered = 0
        
    def set_angle(self, angle:int) -> None:
        if(not(self.enabled)):
            print("Arm disabled")
            return
        elif(self.position == angle):
            
            return
        elif(not(time.time()-self.update_rate > self.last_triggered)): #rate limiter
            print("rate limit reached")
            return
        elif(not(self.min <= angle <= self.max)):
            print("Arm "+self.name+" limit reached")    
            self.logger.warn("Arm "+self.name+" limit reached")
            return

        self.rover.pwm_controller.set_servo(self.pin, angle)
        self.position = angle
        self.last_triggered=time.time()
        self.rover.communication.send_telemetry({"arm_"+self.name: angle})
        print(self.name+":"+str(angle))
        

    def increase_angle(self):
        self.set_angle(self.position+1)

    def decrease_angle(self):
        self.set_angle(self.position-1)

    def set_enabled(self,boolean:bool):
        self.enabled = boolean
        self.rover.pwm_controller.set_no_pulse(self.pin)

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"arm_"+self.name: self.position})