import logging
from Motor import Motor
from Servo import Servo
import math

class Movement:

    motor_one: Motor
    motor_two: Motor
    motor_three: Motor
    motor_four: Motor

    servo_one: Servo
    servo_two: Servo
    servo_three: Servo
    servo_four: Servo

    enabled: bool
    steering_mode: int
    speed: float
    steering: float

    def __init__(self, rover) -> None:
        self.logger = logging.getLogger(__name__)
        self.rover = rover
        self.motor_one = Motor(rover, "motor_one", 50,  19, 26)
        self.motor_two = Motor(rover, "motor_two", 53,  12, 16)
        self.motor_three = Motor(rover, "motor_three", 56, 8, 7)
        self.motor_four = Motor(rover, "motor_four", 59, 1, 13)

        self.steering_mode = 0
        self.steering = 0
        self.servo_one = Servo(rover, "wheel_one", 110, 0, 0, 180)
        self.servo_two = Servo(rover, "wheel_two", 111, 1, 0, 180)
        self.servo_three = Servo(rover, "wheel_three", 112, 2, 0, 180)
        self.servo_four = Servo(rover, "wheel_four", 113, 3, 0, 180)

        self.set_enabled(True)
        self.set_movement_mode(0)
        self.set_speed(0.5)

    def set_enabled(self, enabled: bool):
        self.motor_one.enable() if enabled else self.motor_one.disable()
        self.motor_two.enable() if enabled else self.motor_two.disable()
        self.motor_three.enable() if enabled else self.motor_three.disable()
        self.motor_four.enable() if enabled else self.motor_four.disable()

        self.servo_one.set_enabled(enabled)
        self.servo_two.set_enabled(enabled)
        self.servo_three.set_enabled(enabled)
        self.servo_four.set_enabled(enabled)

        self.enabled = enabled
        self.logger.info("Movement Enabled" if enabled else "Movement Disabled")
        self.rover.communication.send_telemetry({"48": int(enabled)})

    def set_movement_mode(self, steering_mode: int):
        if not self.enabled:
            self.logger.warn("Cannot change steering mode while disarmed")
            return
        
        self.all_stop()
        self.steering_mode = steering_mode
        self.rover.communication.send_telemetry({"115": self.steering_mode})
        self.set_steering(0, setup=True)

    def set_steering(self, steering, setup = False):
        self.steering = steering
        if self.steering_mode == 0:
            self.steering_mode_one(setup)
        elif self.steering_mode == 1:
            self.steering_mode_two(setup)
        elif self.steering_mode == 2:
            self.steering_mode_three(setup)
        
    def run_steering_mode(self, speed: float):
        if abs(speed) < 0.2:
            self.all_stop()
            return
        
        if self.steering_mode == 0:
            self.set_speed(abs(speed))

            if(speed>0):
                self.all_forward()
            else:
                self.all_backward()

            self.motor_one.set_speed(self.speed)
            self.motor_two.set_speed(self.speed)
            self.motor_three.set_speed(self.speed)
            self.motor_four.set_speed(self.speed)


        elif self.steering_mode == 1:
            self.set_speed(abs(speed))

            self.motor_one.set_speed(self.speed)
            self.motor_two.set_speed(self.speed)
            self.motor_three.set_speed(self.speed)
            self.motor_four.set_speed(self.speed)

        elif self.steering_mode == 2:
            
            if(speed>0):
                if(226 <= self.steering <= 360 or 0 <= self.steering <= 44):
                    self.motor_one.set_forward()
                    self.motor_three.set_forward()
                else:
                    self.motor_one.set_backward()
                    self.motor_three.set_backward()

                if(315 <= self.steering <= 360 or 0 <= self.steering <= 135):
                    self.motor_two.set_forward()
                    self.motor_four.set_forward()
                else:
                    self.motor_two.set_backward()
                    self.motor_four.set_backward()
            else:
                if(226 <= self.steering <= 360 or 0 <= self.steering <= 44):
                    self.motor_one.set_backward()
                    self.motor_three.set_backward()
                else:
                    self.motor_one.set_forward()
                    self.motor_three.set_forward()

                if(315 <= self.steering <= 360 or 0 <= self.steering <= 135):
                    self.motor_two.set_backward()
                    self.motor_four.set_backward()
                else:
                    self.motor_two.set_forward()
                    self.motor_four.set_forward()

            self.set_speed(abs(speed))
            self.motor_one.set_speed(self.speed)
            self.motor_two.set_speed(self.speed)
            self.motor_three.set_speed(self.speed)
            self.motor_four.set_speed(self.speed)

    # so there is a triangle and steering is distance from wheel pivot point
    def steering_mode_one(self, setup = False):

        if self.steering == 0:
            self.set_wheels_angles(0, 0, 0, 0)
            return
        elif -45 < self.steering < 0:
            self.steering = -45
        elif 0 < self.steering < 45:
            self.steering = 45

        VERT_DIST_FROM_CENTER = 20
        HORIZ_DIST_FROM_CENTER = 20
        STEERING_DISTANCE = self.steering

        wheel_one_angle = 0
        wheel_two_angle = 0
        wheel_three_angle = 0
        wheel_four_angle = 0

        if STEERING_DISTANCE > 0:
            wheel_one_angle = 90 - math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
            wheel_two_angle = 90 - math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
            wheel_three_angle = 270 + math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
            wheel_four_angle = 270 + math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
        else:
            wheel_one_angle = 270 + abs(math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))
            wheel_two_angle = 270 + abs(math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))
            wheel_three_angle = 90 -  abs(math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))
            wheel_four_angle = 90 -  abs(math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))

        self.set_wheels_angles(wheel_one_angle, wheel_two_angle, wheel_three_angle, wheel_four_angle)




    def steering_mode_two(self, setup = False):
        self.set_wheels_angles(44, 315, 315, 45)
        if self.steering < 0:
            self.motor_one.set_backward()
            self.motor_two.set_forward()
            self.motor_three.set_backward()
            self.motor_four.set_forward()
        elif self.steering > 0 or setup:
            self.motor_one.set_forward()
            self.motor_two.set_backward()
            self.motor_three.set_forward()
            self.motor_four.set_backward()

    def steering_mode_three(self, setup = False):
        if(226 <= self.steering <= 360 or 0 <= self.steering <= 44):
            self.motor_one.set_forward()
            self.motor_three.set_forward()
        else:
            self.motor_one.set_backward()
            self.motor_three.set_backward()

        if(315 <= self.steering <= 360 or 0 <= self.steering <= 135):
            self.motor_two.set_forward()
            self.motor_four.set_forward()
        else:
            self.motor_two.set_backward()
            self.motor_four.set_backward()
        self.set_wheels_angles(self.steering, self.steering, self.steering, self.steering)

    #https://www.visnos.com/demos/basic-angles
    def set_wheels_angles(self, angle_one: float, angle_two: float, angle_three: float, angle_four: float, temp_override: bool = False ):
        angle_one = (angle_one - 45) % 360
        angle_two = (angle_two + 45) % 360
        angle_three = (angle_three - 45) % 360
        angle_four = (angle_four + 45) % 360

        if not 0 <= angle_one <= 180:
            angle_one -= 180

        if not 0 <= angle_two <= 180:
            angle_two -= 180
        
        if not 0 <= angle_three <= 180:
            angle_three -= 180
        
        if not 0 <= angle_four <= 180:
            angle_four -= 180

        angle_one = round(angle_one,0)
        angle_two = round(angle_two,0)
        angle_three = round(angle_three,0)
        angle_four = round(angle_four,0)

        self.servo_one.set_angle(angle_one, temp_override)
        self.servo_two.set_angle(angle_two, temp_override)
        self.servo_three.set_angle(angle_three, temp_override)
        self.servo_four.set_angle(angle_four, temp_override)
        
        
    def set_speed(self, speed: float):
        speed = min(speed, 0.4)
        self.speed = float(speed)
        self.rover.communication.send_telemetry({"49": speed})

    def left_forward(self):
        self.motor_one.set_forward()
        self.motor_three.set_forward()
        self.motor_one.set_speed(self.speed)
        self.motor_three.set_speed(self.speed)

    def left_stop(self):
        self.motor_one.set_speed(0, override=True)
        self.motor_three.set_speed(0, override=True)

    def left_backward(self):
        self.motor_one.set_backward()
        self.motor_three.set_backward()
        self.motor_one.set_speed(self.speed)
        self.motor_three.set_speed(self.speed)

    def right_forward(self):
        self.motor_two.set_forward()
        self.motor_four.set_forward()
        self.motor_four.set_speed(self.speed)
        self.motor_two.set_speed(self.speed)

    def right_stop(self):
        self.motor_two.set_speed(0, override=True)
        self.motor_four.set_speed(0, override=True)

    def right_backward(self):
        self.motor_two.set_backward()
        self.motor_four.set_backward()
        self.motor_four.set_speed(self.speed)
        self.motor_two.set_speed(self.speed)

    def all_forward(self):
        self.motor_one.set_forward()
        self.motor_two.set_forward()
        self.motor_three.set_forward()
        self.motor_four.set_forward()

        self.motor_one.set_speed(self.speed)
        self.motor_two.set_speed(self.speed)
        self.motor_three.set_speed(self.speed)
        self.motor_four.set_speed(self.speed)

    def all_stop(self):
        self.motor_one.set_speed(0, override=True)
        self.motor_two.set_speed(0, override=True)
        self.motor_three.set_speed(0, override=True)
        self.motor_four.set_speed(0, override=True)

    def all_backward(self):
        self.motor_one.set_backward()
        self.motor_two.set_backward()
        self.motor_three.set_backward()
        self.motor_four.set_backward()

        self.motor_one.set_speed(self.speed)
        self.motor_two.set_speed(self.speed)
        self.motor_three.set_speed(self.speed)
        self.motor_four.set_speed(self.speed)

    def send_all_telem(self):
        self.motor_one.send_all_telem()
        self.motor_two.send_all_telem()
        self.motor_three.send_all_telem()
        self.motor_four.send_all_telem()
