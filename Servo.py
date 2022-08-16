import logging
import time
import RPi.GPIO as GPIO
import threading


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
        self.permanent_overide = False
        self.position = 0
        self.update_rate = 0.0001
        self.last_triggered = 0
        self.lock = threading.Lock()
        
    def set_angle(self, angle:int, temp_override:bool = False) -> None:
        if(not(self.enabled)):
            self.logger.error("Cannot move servo while it disarmed")
            return
        elif((self.position == angle) and (not temp_override) and (not self.permanent_overide)):
            return
        elif((not(time.time()-self.update_rate > self.last_triggered))  and (not temp_override) and (not self.permanent_overide)): #rate limiter
            print("rate limit reached")
            return
        elif((not(self.min <= angle <= self.max))  and (not temp_override) and (not self.permanent_overide)):
            self.logger.warn("Arm '"+self.name+"' limit reached")
            return
        
        self.rover.pwm_controller.set_servo(self.pin, angle)
        self.position = angle
        self.last_triggered=time.time()
        self.rover.communication.send_telemetry({"arm_"+self.name: angle})


    def set_angle_with_delay(self, angle:int, steps:int, delay:float):
        if(not(self.enabled)):
            self.logger.error("Cannot move servo while it disarmed")
            return

        self.logger.info("Executing servo movment on '"+self.name+"' for "+str(abs((angle-self.position)/steps)*delay)+" seconds")
        if self.position > angle:
            angle-=1
            steps= -steps
        else:
            angle+=0
        for i in range(self.position,angle,steps):
            if(not(self.enabled)):
                self.logger.error("Cancelling operaition as servo was disarmed")
                return
            self.rover.pwm_controller.set_servo(self.pin, i)
            self.position = i
            self.last_triggered=time.time()
            self.rover.communication.send_telemetry({"arm_"+self.name: i})
            time.sleep(delay)


        self.rover.pwm_controller.set_servo(self.pin, angle)
        self.position = angle
        self.last_triggered=time.time()
        self.rover.communication.send_telemetry({"arm_"+self.name: angle})
        self.logger.info("Execution on '"+self.name+"' servo complete")
    
    def set_permanent_override(self, boolean: bool):
        self.permanent_overide = boolean
        self.logger.warning("Manule override enabled on '"+self.name+"'" if boolean else "Manule override disabled on '"+self.name+"'")

    def increase_angle(self):
        self.set_angle(self.position+1)

    def decrease_angle(self):
        self.set_angle(self.position-1)

    def set_enabled(self,boolean:bool):
        self.enabled = boolean
        self.rover.pwm_controller.set_no_pulse(self.pin)

    def send_all_telem(self):
        self.rover.communication.send_telemetry({"arm_"+self.name: self.position})