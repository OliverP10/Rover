import RPi.GPIO as GPIO

left_motor_a: GPIO.PWM = None
left_motor_b: GPIO.PWM = None
right_motor_a: GPIO.PWM = None
right_motor_b: GPIO.PWM = None

# Set up the GPIO
GPIO.setmode(GPIO.BCM)

# Set up the GPIO channels
GPIO.setup(12,GPIO.OUT) # Left Motor A
GPIO.setup(6,GPIO.OUT) # Left Motor B   changed from 13 to 6 as pin 13 is broken
GPIO.setup(18,GPIO.OUT) # Right Motor A
GPIO.setup(19,GPIO.OUT) # Right Motor B

# Set up the PWM channels
left_motor_a = GPIO.PWM(12, 500)
left_motor_b = GPIO.PWM(6, 500)
right_motor_a = GPIO.PWM(18, 500)
right_motor_b = GPIO.PWM(19, 500)

# Start the PWM channels
left_motor_a.start(0)
left_motor_b.start(0)
right_motor_a.start(0)
right_motor_b.start(0)


class Motor:
    left: float
    right: float

def set_motor_speeds(data: Motor):
    global motor_status
    motor_status = data

    data.left = data.left * 100
    data.right = data.right * 100

    if(data.left >= 0):
        left_motor_a.ChangeDutyCycle(data.left)
        left_motor_b.ChangeDutyCycle(0)
    else:
        left_motor_a.ChangeDutyCycle(0)
        left_motor_b.ChangeDutyCycle(-data.left)

    if(data.right >= 0):
        right_motor_a.ChangeDutyCycle(data.right)
        right_motor_b.ChangeDutyCycle(0)
    else:
        right_motor_a.ChangeDutyCycle(0)
        right_motor_b.ChangeDutyCycle(-data.right)

print("running...")
while True:
    speed = float(input())
    motor = Motor()
    motor.left = speed
    motor.right = speed
    set_motor_speeds(motor)

# left_motor_a.ChangeDutyCycle(0)
# left_motor_b.ChangeDutyCycle(0)