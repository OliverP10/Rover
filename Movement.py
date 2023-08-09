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
        self.motor_one = Motor(rover, "motor_one", 50,  0, 5)
        self.motor_two = Motor(rover, "motor_two", 53,  13, 6)
        self.motor_three = Motor(rover, "motor_three", 56, 25, 7)
        self.motor_four = Motor(rover, "motor_four", 59, 20, 8)

        self.steering_mode = 0
        self.servo_one = Servo(rover, "wheel_one", 110, 6, 0, 180)
        self.servo_two = Servo(rover, "wheel_two", 111, 6, 0, 180)
        self.servo_three = Servo(rover, "wheel_three", 112, 6, 0, 180)
        self.servo_four = Servo(rover, "wheel_four", 113, 6, 0, 180)

        self.set_enabled(True)
        self.set_steering_mode(1)
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

    def set_steering_mode(self, steering_mode: int):
        self.all_stop()
        self.steering_mode = steering_mode

        if self.steering_mode == 0:
            self.steering_mode_one(self.steering_mode)
        elif self.steering_mode == 1:
            self.steering_mode_two()
        elif self.steering_mode == 2:
            self.steering_mode_three(self.steering_mode)
        
        self.rover.communication.send_telemetry({"115": self.steering_mode})

    def run_steering_mode(self, speed: float):
        if abs(speed) < 0.2:
            self.all_stop()
            return
        
        if self.steering_mode == 0:
            self.set_speed(abs(speed))
            self.all_forward() if speed > 0 else self.all_backward()

        elif self.steering_mode == 1:
            self.set_speed(abs(speed))
            self.left_forward() if speed > 0 else self.left_backward()
            self.right_forward() if speed < 0 else self.right_backward()

        elif self.steering_mode == 2:
            self.set_speed(abs(speed))

            if(225 <= self.steering <= 45):
                self.motor_one.set_forward()
                self.motor_four.set_forward()
            else:
                self.motor_one.set_backward()
                self.motor_four.set_backward()
            self.motor_one.set_speed(self.speed)
            self.motor_four.set_speed(self.speed)

            if(315 <= self.steering <= 135):
                self.motor_two.set_forward()
                self.motor_three.set_forward()
            else:
                self.motor_two.set_backward()
                self.motor_three.set_backward()
            self.motor_two.set_speed(self.speed)
            self.motor_three.set_speed(self.speed)



    # so there is a triangle and steering is distance from wheel pivot point
    def steering_mode_one(self, steering: float):
        if -30 < steering < 30:
            self.set_wheels_angles(0, 0, 0, 0)
            return

        VERT_DIST_FROM_CENTER = 20
        HORIZ_DIST_FROM_CENTER = 20
        STEERING_DISTANCE = steering

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

    def steering_mode_two(self):
        self.set_wheels_angles(45, 315, 315, 45)

    def steering_mode_three(self, steering: float):
        self.set_wheels_angles(steering, steering, steering, steering)

    #https://www.visnos.com/demos/basic-angles
    def set_wheels_angles(self, angle_one: float, angle_two: float, angle_three: float, angle_four: float):
        
        
        print(angle_one)
        print(angle_two)
        print(angle_three)
        print(angle_four)
        print("")

        # loop wheel rotaition if they go beyond limits
        if(45 < angle_one < 255):
            angle_one = (angle_one + 180) % 360
            angle_one -= 225

        if(45 < angle_four < 255):
            angle_four = (angle_four + 180) % 360
            angle_four -= 225

        if(135 < angle_two < 315):
            angle_two -= 180
        else:
            angle_two = (angle_two + 180) % 360
            angle_two -= 45


        if(135 < angle_three < 315):
            angle_three = (angle_three + 180) % 360
            angle_three -= 315

        angle_one = (angle_one - 45) % 360
        angle_two = (angle_two + 45) % 360
        angle_three = (angle_three + 45) % 360
        angle_four = (angle_four - 45) % 360

        print(angle_one)
        print(angle_two)
        print(angle_three)
        print(angle_four)

        self.servo_one.set_angle(angle_one)
        self.servo_two.set_angle(angle_two)
        self.servo_three.set_angle(angle_three)
        self.servo_four.set_angle(angle_four)
        
        
    def set_speed(self, speed: float):
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

        self.motor_one.set_forward()
        self.motor_two.set_forward()
        self.motor_three.set_forward()
        self.motor_four.set_forward()

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
