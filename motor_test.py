import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

class Motor:
	'''
	A Motor. YEE.
	'''
	def __init__(self, p1, p2, pwm):
		'''
		set up the motor pin assignments
		'''
		self.p1 = p1
		self.p2 = p2
		self.pwm = pwm
		GPIO.setup(self.p1, GPIO.OUT)
		GPIO.setup(self.p2, GPIO.OUT)
		PWM.start(self.pwm,0,50,0)

	def set(self, speed, forward):
		'''
		set motor speed, direction
		speed is a number from 1 to 50
		forward is True if you want the motor to spin forward.
		'''
		if forward == True:
			GPIO.output(self.p1, GPIO.HIGH)
			GPIO.output(self.p2, GPIO.LOW)
		else:		
			GPIO.output(self.p1, GPIO.LOW)
			GPIO.output(self.p2, GPIO.HIGH)			

		PWM.set_duty_cycle(self.pwm, speed) 

PWM_front_drive = "P9_14"
PWM_rear_drive = "P9_21"
PWM_steer = "P9_16"
STANDBY = "P9_23"

fd1, fd2 = "P9_11", "P9_27"
rd1, rd2 = "P9_15", "P9_25"
steer_1, steer_2 = "P9_17", "P9_18"

height = 240
width = 360
STEP = 3

thresh_1x = width*1.0/STEP
thresh_2x = width*2.0/STEP
thresh_1y = height*1.0/STEP
thresh_2y = height*2.0/STEP

# intialize stuff
GPIO.output(STANDBY, GPIO.HIGH)
front = Motor(fd1, fd2, PWM_front_drive)
rear = Motor(rd1, rd2, PWM_rear_drive)
steer = Motor(steer_1, steer_2, PWM_steer)

front.set(25, True)
