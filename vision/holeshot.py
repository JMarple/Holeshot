import cv2
import serial
import time
import trackObjects
import findblobs
import coneCalculations

class jetsonRobot:
    
    def __init__(self):
        pass

    def connect(self):
        self.ser = serial.Serial(
            port = '/dev/ttyACM0',
            baudrate=115200,
            parity = serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        # The robot should be connected now
        #self.ser.write('t50!')

        #self.ser.close()
    
    def waitForButton(self):

        line = []
        print "Waiting for button..."
        while True:
            for c in self.ser.read():
                # If any data is sent back, good to go? lol    
                return

        print "Found button!"

    def closeSerial(self):
        self.ser.close()

if __name__ == "__main__":
    j = jetsonRobot()   
    j.connect()

    j.waitForButton()
    
    turnPID = coneCalculations.jetsonPID(0.05, 0, 0)

    t = trackObjects.trackObjects()
    
    cap = cv2.VideoCapture(0)   
    video = cv2.VideoWriter("video.avi", cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), 25, (640, 480))

    j.ser.write("t38!")

    while (cap.isOpened()):
        
        j.ser.write("t38!")

        ret, frame = cap.read()

        labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        objects, someimg = findblobs.findBlobs(labImage, True)          

        t.update(objects)

        targetPos = coneCalculations.getTargetPosition(t.getObjects())
    
        height, width = labImage.shape[:2]

        error = targetPos[0] - width/2
    
        turnFeedback = int(turnPID.update(error))
        if (turnFeedback > 50): turnFeedback = 50
        if (turnFeedback < -50): turnFeedback = -50

        turnFeedback += 50  

        j.ser.write("s" + str(turnFeedback) + "!")
    
        print "Error = " + str(error)
        cv2.line(someimg, (width/2, height), targetPos, (255, 0, 255), 2)

        for obj in t.getObjects():
            rect = obj.getRect()
            cv2.rectangle(someimg, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 255), 2)
            cv2.putText(someimg, str(obj.newid), (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))
    
        cv2.imshow('testimage', someimg)    
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()   
    video.release()
    j.closeSerial()
