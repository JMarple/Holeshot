#!/usr/bin/python

import cv2
import numpy as np

cv2.namedWindow('testimage')

low = np.array([0, 0, 0])
high = np.array([255, 255, 255])

def updateImage(x):
    pass

#cv2.createTrackbar('Lh', 'testimage', 0, 255, updateImage)
cv2.createTrackbar('Ah', 'testimage', 0, 255, updateImage)
cv2.createTrackbar('Bh', 'testimage', 0, 255, updateImage)
#cv2.createTrackbar('Ll', 'testimage', 0, 255, updateImage)
cv2.createTrackbar('Al', 'testimage', 0, 255, updateImage)
cv2.createTrackbar('Bl', 'testimage', 0, 255, updateImage)

im = cv2.imread("test.jpg")

labImage = cv2.cvtColor(im, cv2.COLOR_BGR2LAB);

mask = cv2.inRange(labImage, low, high)
output = cv2.bitwise_and(labImage, labImage, mask = mask)

#cv2.setTrackbarPos('Lh', 'testimage', 255)
cv2.setTrackbarPos('Ah', 'testimage', 255)
cv2.setTrackbarPos('Bh', 'testimage', 255)

while(1):
    low[0] = 0#cv2.getTrackbarPos('Ll', 'testimage')
    low[1] = cv2.getTrackbarPos('Al', 'testimage')
    low[2] = cv2.getTrackbarPos('Bl', 'testimage')
    high[0] = 255#cv2.getTrackbarPos('Lh', 'testimage')
    high[1] = cv2.getTrackbarPos('Ah', 'testimage')
    high[2] = cv2.getTrackbarPos('Bh', 'testimage')
    
    mask = cv2.inRange(labImage, low, high)
    output = cv2.bitwise_and(im, im, mask = mask)
    weighted = cv2.addWeighted(output, 0.9, im, 0.1, 0) 
    cv2.imshow('testimage', weighted)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    
cv2.destroyAllWindows()
