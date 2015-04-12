'''
fish_tracker.py
Author:
	Ankush Gola
'''

import cv2
import numpy as np
from iir_filter import IIRFilter
from collections import deque

class FishTracker:
	"""
	FishTracker is a class that implements fish tracking via either svm or hsv masking
	"""

	def __init__(self, cap=0, morph_close=5, morph_open=5, filter_tap=0, height=240, width=360, median=5):
		"""
		return an instance of FishTracker
		cap: which video capture to use
		morph_close: size of morphological close mask
		morph_open: size of morphological open mask
		gauss: size of gaussian blur mask
		filter_tap: weight in iir filter
		"""
		self.cap = cv2.VideoCapture(cap)
		self.height = height
		self.width = width
		self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 360)
		self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
		self.h_lo, self.s_lo, self.v_lo = 0, 0, 0
		self.h_hi, self.s_hi, self.v_hi = 100, 100, 100
		self.hsv_lower = np.array([self.h_lo, self.s_lo, self.v_lo])
		self.hsv_upper = np.array([self.h_hi, self.s_hi, self.v_hi])
		self.kernel_close = np.ones((morph_close, morph_close),np.uint8)
		self.kernel_open = np.ones((morph_open, morph_open),np.uint8)
		self.iir = None # will update this in detect_ball
		self.filter_tap = filter_tap
		self.buffer_x = deque(maxlen=5)
		self.buffer_y = deque(maxlen=5)
		self.median = median

	def get_hsv_lo(self):
		"""
		return hsv lower bounds as np array
		"""
		return self.hsv_lower

	def get_hsv_hi(self):
		"""
		return hsv upper bounds as np array
		"""
		return self.hsv_upper

	def set_hsv_hi(self, (h, s, v)):
		"""
		set the hsv upper bounds as h, s, v
		"""
		self.h_hi, self.s_hi, self.v_hi = h, s, v
		self.hsv_upper = np.array([self.h_hi, self.s_hi, self.v_hi])

	def get_hsv_lo(self):
		"""
		return hsv upper bounds as np array
		"""
		return self.hsv_lower

	def set_hsv_lo(self, (h, s, v)):
		"""
		set the hsv upper bounds as h, s, v
		"""
		self.h_lo, self.s_lo, self.v_lo = h, s, v
		self.hsv_lower = np.array([self.h_lo, self.s_lo, self.v_lo])

	def release_cap(self):
		"""
		release the cap
		"""
		self.cap.release()

	def detect_fish(self, show_res=True, strat='CENT', morph=True):
		"""
		detect the ball in the current frame and return the x, y position of fish
		show_res: also return the resulting image with the detected circle drawn
		strat: which detector to use (TODO)
		morph: perform morphological operations
		"""
		_, frame = self.cap.read() # read a frame
		hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) # convert to HSV space
		mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)

		if morph:
			# do dilation and erosion
			mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel_close)
			mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel_open)

		moments = cv2.moments(mask, True)
		cx = moments['m10'] / moments['m00'] if moments['m00'] != 0 else self.width/2
		cy = moments['m01'] / moments['m00'] if moments['m00'] != 0 else self.height/2

		if self.iir == None:
			# create new IIRFilter if first run
			self.iir = IIRFilter(np.float32((cx, cy)), self.filter_tap)
		else:
			self.iir.update(np.float32((cx, cy)))

		[x, y] = self.iir.state()
		
		if len(self.buffer_x) < self.median:
			self.buffer_x.append(x)
			self.buffer_y.append(y)
			[x, y] = [self.width/2, self.height/2]
		else:
			self.buffer_x.popleft()
			self.buffer_y.popleft()
			self.buffer_x.append(x)
			self.buffer_y.append(y)
			[x, y] = np.median(self.buffer_x), np.median(self.buffer_y)


		if show_res:
			result = cv2.bitwise_and(frame,frame,mask = mask)
			cv2.circle(result,(int(cx),int(cy)),2,(0,255,0),3)
		else:
			result = None

		return (result, (x, y))



"""
Testing
"""

def getzone(x, y, thresh_1x, thresh_2x, thresh_1y, thresh_2y):

	if x < thresh_1x and y < thresh_1y:
		return 'FORWARD_RIGHT'
	elif x < thresh_1x and (y >= thresh_1y and y < thresh_2y):
		return 'FORWARD_CENTER'
	elif x < thresh_1x and y >= thresh_2y:
		return 'FORWARD_LEFT'
	elif (x >= thresh_1x and x < thresh_2x) and y < thresh_1y:
		return 'STALL_RIGHT'
	elif (x >= thresh_1x and x < thresh_2x) and (y >= thresh_1y and y < thresh_2y):
		return 'STALL_CENTER'
	elif (x >= thresh_1x and x < thresh_2x) and y >= thresh_2y:
		return 'STALL_LEFT'
	elif x >= thresh_2x and y < thresh_1y:
		return 'READ_RIGHT'
	elif x >= thresh_2x and (y >= thresh_1y and y < thresh_2y):
		return 'REAR_CENTER'
	elif x >= thresh_2x and y >= thresh_2y:
		return 'REAR_LEFT'

def test():
	height = 240
	width = 360
	STEP = 3

	thresh_1x = width*1.0/STEP
	thresh_2x = width*2.0/STEP
	thresh_1y = height*1.0/STEP
	thresh_2y = height*2.0/STEP

	'''
	H_LOW = 5, S_LOW = 218, V_LOW = 189
	H_HI = 15, S_HI = 255, V_HI = 255
	'''

	ft = FishTracker(cap=0, filter_tap=0.5, height=height, width=width)
	ft.set_hsv_lo((5, 218, 189))
	ft.set_hsv_hi((15, 255, 255))

	while True:
		(res, state) = ft.detect_fish(show_res=True)
		#print state
		x, y = state
		print getzone(int(x), int(y), thresh_1x, thresh_2x, thresh_1y, thresh_2y)
		cv2.imshow('result',res)
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break
	ft.release_cap()

test()
