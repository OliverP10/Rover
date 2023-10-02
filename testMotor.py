import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pwm_channel_pin = 12 #19
dir_channel_pin = 16 #26

GPIO.setup(pwm_channel_pin, GPIO.OUT)
GPIO.setup(dir_channel_pin, GPIO.OUT)

pwm_channel = GPIO.PWM(pwm_channel_pin, 500)
# dir_channel = GPIO.PWM(dir_channel_pin, 500)


pwm_channel.start(0)
GPIO.output(dir_channel_pin, GPIO.HIGH)

print("Running: ")
while True:
    speed = float(input())
    pwm_channel.ChangeDutyCycle(speed*100)
