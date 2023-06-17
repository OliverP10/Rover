from adafruit_servokit import ServoKit
import board
import busio
from adafruit_pca9685 import PCA9685


kit = ServoKit(channels=16)
pca = PCA9685(busio.I2C(board.SCL, board.SDA))
pca.frequency = 50  # Set the desired frequency


# kit.servo[0].actuation_range = 270
kit.servo[0].set_pulse_width_range(500, 2600)
# kit.continuous_servo[4].set_pulse_width_range(-19000, 19000)

while True:
    number = float(input())

    if number == -1:
        kit.servo[0].angle = None
        print("setting no pulse")
    else:
        kit.servo[0].angle = number  
        #kit.continuous_servo[motor_pin].throttle = number # 0 to 1
        print("set number to: "+str(number))
