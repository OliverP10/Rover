
from adafruit_servokit import ServoKit
import time

kit:ServoKit = ServoKit(channels=16)

kit.servo[0].set_pulse_width_range(500, 2600)

kit.servo[0].angle = 0


# kit.continuous_servo[0].set_pulse_width_range(-19000, 19000)

# kit.continuous_servo[0].throttle = 0


# for i in range(0,100,1):
#     #kit.servo[0].angle = i
#     kit.continuous_servo[0].throttle = i/100
#     print(i/100)
#     time.sleep(0.1)

#just put into class