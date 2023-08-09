import logging
import time
import RPi.GPIO as GPIO
from threading import Thread, Event

class Servo:
    logger: any
    rover: any
    name: str
    telemetry_id: int
    pin: int
    enabled: bool
    position: int
    update_rate: int
    last_triggered: int

    run_clockwise: Event
    run_counter_clockwise: Event
    turn_clockwise_thread: Thread
    turn_counter_clockwise_thread1  : Thread

    run_: Event

    def __init__(self, rover: any, name: str, telemetry_id: int, pin: int, min: int, max: int) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.name = name
        self.telemetry_id = telemetry_id
        self.pin = pin
        self.min = min
        self.max = max
        self.enabled = False
        self.permanent_overide = False
        self.position = 0
        self.update_rate = 0.0001
        self.last_triggered = 0

   
        self.run_clockwise = Event()
        self.run_clockwise.clear()
        self.run_counter_clockwise = Event()
        self.run_counter_clockwise.clear()
        self.turn_clockwise_thread = Thread(target = self.run_clockwise_thread).start()
        self.turn_counter_clockwise_thread = Thread(target = self.run_counter_clockwise_thread).start()

    def set_angle(self, angle: int, temp_override: bool = False) -> None:
        check_passed: bool = True
        if angle == None:
            self.logger.debug("Cannot move servo to position None")
            check_passed = False
        elif (not (self.enabled)):
            self.logger.error("Cannot move servo while it disarmed")
            check_passed = False
        elif ((self.position == angle) and (not temp_override) and (not self.permanent_overide)):
            self.logger.debug("Angle already set")
            check_passed = False
        elif ((not (time.time()-self.update_rate > self.last_triggered)) and (not temp_override) and (not self.permanent_overide)):  # rate limiter
            self.logger.debug("Rate limit reached")
            check_passed = False
        elif ((not (self.min <= angle <= self.max)) and (not temp_override) and (not self.permanent_overide)):
            self.logger.warn("Arm '"+self.name+"' limit reached")
            self.logger.debug("{min} < {angle} < {max}".format(min=self.min, angle=angle, max=self.max))
            check_passed = False

        if check_passed:
            self.rover.pwm_controller.set_servo(self.pin, angle)
            self.position = angle
            self.last_triggered = time.time()
            self.logger.debug("Set "+self.name+" angle: "+ str(angle))
        
        self.rover.communication.send_telemetry({self.telemetry_id: self.position})

    def set_angle_with_delay(self, angle: int, steps: int, delay: float):
        if not self.enabled:
            self.logger.error("Cannot move servo while it disarmed")
            return

        self.logger.info("Executing servo movment on '"+self.name+"' for " +
                         str(abs((angle-self.position)/steps)*delay)+" seconds")
        if self.position > angle:
            angle -= 1
            steps = -steps
        else:
            angle += 0
        for i in range(self.position, angle, steps):
            if (not (self.enabled)):
                self.logger.error("Cancelling operaition as servo was disarmed")
                return
            self.rover.pwm_controller.set_servo(self.pin, i)
            self.position = i
            self.last_triggered = time.time()
            self.rover.communication.send_telemetry({self.telemetry_id: self.position})
            time.sleep(delay)

        self.rover.pwm_controller.set_servo(self.pin, angle)
        self.position = angle
        self.last_triggered = time.time()
        self.rover.communication.send_telemetry({self.telemetry_id: self.position})
        self.logger.info("Execution on '"+self.name+"' servo complete")

    def set_permanent_override(self, boolean: bool):
        self.permanent_overide = boolean
        self.logger.warning("Manule override enabled on '"+self.name +
                            "'" if boolean else "Manule override disabled on '"+self.name+"'")

    def increase_angle(self, incrementBy: int = 1):
        self.set_angle(self.position+incrementBy)

    def decrease_angle(self, incrementBy: int = 1):
        self.set_angle(self.position-incrementBy)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if enabled:
            self.set_angle(self.position)
        else:
            self.rover.pwm_controller.set_no_pulse(self.pin)
            self.stop_turn()

    def turn_clockwise(self):
        self.run_counter_clockwise.clear()
        self.run_clockwise.set()

    def run_clockwise_thread(self):
        while True:
            if not self.run_clockwise.is_set():
                self.run_clockwise.wait()

            self.increase_angle(1)
            time.sleep(0.1)

    def turn_counter_clockwise(self):
        self.run_clockwise.clear()
        self.run_counter_clockwise.set()

    def run_counter_clockwise_thread(self):
        while True:
            if not self.run_counter_clockwise.is_set():
                self.run_counter_clockwise.wait()

            self.decrease_angle(1)
            time.sleep(0.1)

    def stop_turn(self):
        self.run_clockwise.clear()
        self.run_counter_clockwise.clear()

    def send_all_telem(self):
        self.rover.communication.send_telemetry({self.telemetry_id: self.position})
