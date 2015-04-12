#!/usr/bin/python

import cv2
import numpy as np

cap = cv2.VideoCapture(1)

'''
H_LOW = 0, S_LOW = 145, V_LOW = 134
H_HI = 5, S_HI = 255, V_HI = 253
'''
'''
H_LOW = 0, S_LOW = 135, V_LOW = 47
H_HI = 19, S_HI = 230, V_HI = 76
'''
def centroid(img):
    sig_x, sig_y = 0, 0
    white = 0
    (M, N) = img.shape
    for i in xrange(M):
        for j in xrange(N):
            if img[i, j] == 1:
                sig_x += i
                sig_y += j
                white += 1

    if white == 0:
        return None, None

    xc = sig_x/white
    yc = sig_y/white

    return (xc, yc)

def nothing(x):
    pass
# Creating a window for later use
cv2.namedWindow('result')

# Starting with 100's to prevent error while masking
h,s,v = 100,100,100

# Creating track bar
cv2.createTrackbar('h_low', 'result',0,255,nothing)
cv2.createTrackbar('s_low', 'result',0,255,nothing)
cv2.createTrackbar('v_low', 'result',0,255,nothing)

cv2.createTrackbar('h_hi', 'result',0,255,nothing)
cv2.createTrackbar('s_hi', 'result',0,255,nothing)
cv2.createTrackbar('v_hi', 'result',0,255,nothing)

cv2.createTrackbar('morph', 'result',0,1,nothing)
cv2.createTrackbar('smooth', 'result',1,15,nothing)

while(1):

    _, frame = cap.read()

    #converting to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # get info from track bar and appy to result
    h = cv2.getTrackbarPos('h_low','result')
    s = cv2.getTrackbarPos('s_low','result')
    v = cv2.getTrackbarPos('v_low','result')

    h_hi = cv2.getTrackbarPos('h_hi','result')
    s_hi = cv2.getTrackbarPos('s_hi','result')
    v_hi = cv2.getTrackbarPos('v_hi','result')

    morph = cv2.getTrackbarPos('morph','result')
    smooth = cv2.getTrackbarPos('smooth','result')

    # Normal masking algorithm
    lower = np.array([h, s, v])
    upper = np.array([h_hi, s_hi, v_hi])
    

    print("H_LOW = " + str(h) + ", " + "S_LOW = " + str(s) + ", " + "V_LOW = " + str(v))
    print("H_HI = " + str(h_hi) + ", " + "S_HI = " + str(s_hi) +", " + "V_HI = " + str(v_hi))

    mask = cv2.inRange(hsv,lower, upper)


    if morph:
        # Do Dilation and Erosion
        kernel_close = np.ones((5,5),np.uint8)
        kernel_open = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)

    moments = cv2.moments(mask, True)
    cx = moments['m10'] / moments['m00'] if moments['m00'] != 0 else 0
    cy = moments['m01'] / moments['m00'] if moments['m00'] != 0 else 0


    result = cv2.bitwise_and(frame,frame,mask = mask)
    cv2.circle(result,(int(cx),int(cy)),2,(0,255,0),3)
    #res = cv2.resize(result,None,fx=1, fy=1)
    cv2.imshow('result',result)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cap.release()

cv2.destroyAllWindows()