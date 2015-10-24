#!/usr/bin/python

import cv2
import numpy as np

# Takes in an LAB image and returns boxes showing where relevant objects are  
def findBlobs(labImage):
   
    orangeLow = np.array([0, 160, 140])
    orangeHigh = np.array([255, 255, 255])

    mask = cv2.inRange(labImage, orangeLow, orangeHigh)
    output = cv2.bitwise_and(labImage, labImage, mask = mask)

    edged = cv2.Canny(output, 30, 200)   
    
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]    
 
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
   
        if peri < 40:
            continue
     
        print len(approx)
        print peri
        print ""

        cv2.drawContours(labImage, [c], -1, (0, 255, 0), 3)
     
    return labImage
     
if __name__ == "__main__":
    img = cv2.imread("../testing/test.jpg")    
    labImage = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        
    output = findBlobs(labImage)
    
    cv2.imshow('testimage', output)
    cv2.waitKey(0)
