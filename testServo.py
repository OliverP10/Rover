from adafruit_servokit import ServoKit
import board
import busio
from adafruit_pca9685 import PCA9685
import time

# BLACK pitch 1: 20 - 180
# BLUE pitch 2: 60 - 130
# GREEN roll: 0 - 180
# RED claw: 28 - 85

kit = ServoKit(channels=16)
pca = PCA9685(busio.I2C(board.SCL, board.SDA))
pca.frequency = 50  # Set the desired frequency

pin = 3

kit.servo[pin].actuation_range = 180
kit.servo[pin].set_pulse_width_range(500, 2500)


def convert_angle(angle):
    angle = (angle + 45) % 360

    if not 0 <= angle <= 180:
        angle -= 180
    return angle


while True:
    #pin = int(input())
    angle = int(input())

    if angle == -1:
        kit.servo[pin].angle = None
        #kit.servo[pin].duty_cycle = 0
        print("setting no pulse")
    else:
        kit.servo[pin].angle = convert_angle(angle)  
        print("set number to: "+str(convert_angle(angle) ))


