from adafruit_servokit import ServoKit
import board
import busio
from adafruit_pca9685 import PCA9685
import time


kit = ServoKit(channels=16)
pca = PCA9685(busio.I2C(board.SCL, board.SDA))
pca.frequency = 50  # Set the desired frequency


kit.servo[0].actuation_range = 270
kit.servo[0].set_pulse_width_range(500, 2600)


while True:
    number = float(input())

    if number == -1:
        kit.servo[0].angle = None
        print("setting no pulse")
    else:
        kit.servo[0].angle = number  
        print("set number to: "+str(number))

