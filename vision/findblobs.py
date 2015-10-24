#!/usr/bin/python

import cv2
import numpy as np

DEBUG = False

# Takes in an LAB image and returns boxes showing where relevant objects are  
def findBlobs(labImage):
   
    orangeLow = np.array([0, 145, 140])
    orangeHigh = np.array([255, 200, 210])

    mask = cv2.inRange(labImage, orangeLow, orangeHigh)
    output = cv2.bitwise_and(labImage, labImage, mask = mask)

    blurredOutput = cv2.blur(output, (25, 25))

    ret, thresh1 = cv2.threshold(blurredOutput, 1, 255, cv2.THRESH_BINARY)

    edged = cv2.Canny(thresh1, 30, 200)   
 
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]    
    
    objs = []
     
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        if peri < 80:
            continue
         
        high = np.array([0,0])
        low = np.array([10000, 10000])

        # Find boundingbox
        for obj in approx:
            if obj[0][0] > high[0]:
                high[0] = obj[0][0]
            if obj[0][1] > high[1]:
                high[1] = obj[0][1]
            if obj[0][0] < low[0]:
                low[0] = obj[0][0]
            if obj[0][1] < low[1]:
                low[1] = obj[0][1] 
        
        objs.append([0, low[0], low[1], high[0], high[1]])    
        
        cv2.drawContours(labImage, [c], -1, (0, 255, 0), 3)
  
    x1 = 1
    x2 = 3
    y1 = 2
    y2 = 4 

    height, width = labImage.shape[:2]
    
    CUTOFF_HEIGHT = 300 # Anything above this height (0 to 300) should not be considered a potentional object

    cv2.rectangle(labImage, (0, CUTOFF_HEIGHT), (width, CUTOFF_HEIGHT), (255, 255, 0), 1)

    for obj in objs:
        if obj[0] != 0: continue
 
        for checkObj in objs:

            if obj is checkObj: continue
            if checkObj[0] != 0: continue # Already found

            # Check if intersecting, if not, check the next one
            if obj[y2] < checkObj[y1]: continue
            if checkObj[y2] < obj[y1]: continue
            if obj[x2] < checkObj[x1]: continue
            if checkObj[x2] < obj[x1]: continue
           
            obj[x1] = min(obj[x1], checkObj[x1])
            obj[x2] = max(obj[x2], checkObj[x2])
            obj[y1] = min(obj[y1], checkObj[y1])
            obj[y2] = max(obj[y2], checkObj[y2])
 
            checkObj[0] = 1 

    for obj in objs:
        if obj[0] != 0: continue
        if obj[y2] < CUTOFF_HEIGHT: continue           

        cv2.rectangle(labImage, (obj[x1], obj[y1]), (obj[x2], obj[y2]), (255,0,0), 1)
 
    return labImage
     
if __name__ == "__main__":
    
    cap = cv2.VideoCapture("../testing/testvideo3.avi")

    while (cap.isOpened()):
        ret, frame = cap.read()
        
        labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        output = findBlobs(labImage)
        
        cv2.imshow('testimage', output)

        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
            
    cap.release() 
