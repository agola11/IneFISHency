'''
fish_control.py
	main program for fishbot

Author:
	Ankush Gola, Joseph Bolling
'''
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
from fish_tracker import FishTracker

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

def getzone(x, y, thresh_1x, thresh_2x, thresh_1y, thresh_2y):
	'''
	get the zone according to the x,y position
	'''
	if x < thresh_1x and y < thresh_1y:
		return 'FORWARD_RIGHT'
	elif x < thresh_1x and (y >= thresh_1y and y < thresh_2y):
		return 'FORWARD_CENTER'
	elif x < thresh_1x and y >= thresh_2y:
		return 'FORWARD_LEFT'
	elif (x >= thresh_1x and x < thresh_2x) and y < thresh_1y:
		return 'STALL_RIGHT'
	elif (x >= thresh_1x and x < thresh_2x) and (y >= thresh_1y and y < thresh_2y):
		return 'NO_FLEX_ZONE'
	elif (x >= thresh_1x and x < thresh_2x) and y >= thresh_2y:
		return 'STALL_LEFT'
	elif x >= thresh_2x and y < thresh_1y:
		return 'READ_RIGHT'
	elif x >= thresh_2x and (y >= thresh_1y and y < thresh_2y):
		return 'REAR_CENTER'
	elif x >= thresh_2x and y >= thresh_2y:
		return 'REAR_LEFT'

def main():
	'''
	main driver for fish control of RC car
	'''
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

	ft = FishTracker(cap=0, filter_tap=0.5, height=height, width=width)
	ft.set_hsv_lo((0, 158, 83))
	ft.set_hsv_hi((29, 255, 218))
	while True:
		(res, state) = ft.detect_fish(show_res=False)
		#print state
		x, y = state
		print getzone(int(x), int(y), thresh_1x, thresh_2x, thresh_1y, thresh_2y)
		#cv2.imshow('result',res)
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break

	ft.release_cap()

main()