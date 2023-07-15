import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pin_channel_1 = 12
pin_channel_2 = 6

GPIO.setup(pin_channel_1, GPIO.OUT)
GPIO.setup(pin_channel_2, GPIO.OUT)

pwm_channel_1 = GPIO.PWM(pin_channel_1, 500)
pwm_channel_2 = GPIO.PWM(pin_channel_2, 500)

pwm_channel_1.start(0.5)
pwm_channel_2.start(0.5)

print("Running: ")
while True:
    speed = float(input())
    pwm_channel_1.ChangeDutyCycle(speed*100)
    pwm_channel_2.ChangeDutyCycle(speed*100)