import cv2
import numpy as np

if __name__ == "__main__":
    
    cap = cv2.VideoCapture("../testing/changingLights.avi")
    previousGreen = None

    kernel = np.ones((5, 5), np.uint8)   

    prevSum = 0
 
    while (cap.isOpened()):
        ret, frame = cap.read()
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower = np.array([200, 0, 200])
        upper = np.array([255, 255, 255])
    
        hsvlower = np.array([0,100,75])
        hsvupper = np.array([100,150,125])

        hsvgreen = cv2.inRange(frame, hsvlower, hsvupper)        

        green = cv2.inRange(frame, lower, upper)

        #green = cv2.dilate(green, kernel, iterations = 1)       
        green = green & hsvgreen
 
        if (previousGreen is not None): 
            diff = hsvgreen & cv2.bitwise_not(previousGreen)
            data = cv2.countNonZero(diff)
            velocity = data - prevSum
            if (velocity > 5000):
                print "GREEN!"
            prevSum = data  
            cv2.imshow('testimage', diff)

        if (previousGreen is None):
            previousGreen = hsvgreen
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
        
