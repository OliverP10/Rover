import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

dir_channel = 5
pwm_channel = 10

dir_pin = GPIO.setup(dir_channel, GPIO.OUT)
pwm_pin = GPIO.setup(pwm_channel, GPIO.OUT)

GPIO.output(dir_channel, GPIO.HIGH)

print("Running: ")
while True:
    speed = float(input())
    pwm_pin.ChangeDutyCycle(speed*100)