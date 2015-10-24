import trackObjects
import findblobs
import cv2

def getTargetPosition(objects):

    if len(objects) < 2: return (-1, -1)

    x = 0
    y = 0

    # Get two largest objects
    for i in range(0, 2):
        center = objects[i].getCenter()
        x += center[0]
        y += center[1]
   
    return (x/2, y/2) 

if __name__ == "__main__":
    t = trackObjects.trackObjects()
    cap = cv2.VideoCapture("../testing/testvideo3.avi")
    
    while (cap.isOpened()):
        ret, frame = cap.read()
        labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        objects, someimg = findblobs.findBlobs(labImage, True)
        t.update(objects)
        t.printObjects()

        targetPos = getTargetPosition(t.getObjects())

        height, width = labImage.shape[:2] 

        cv2.line(someimg, (width/2, height), targetPos, (255, 0, 255), 2) 

        for obj in t.getObjects():
            rect = obj.getRect()
            cv2.rectangle(someimg, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 255), 2) 
            cv2.putText(someimg, str(obj.newid), (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255)) 

        cv2.imshow('testimage', someimg)
            
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
 
    cap.release()
