import cv2
import numpy as np
import pyautogui
import keyboard
import time
from PIL import Image

faceCascade = cv2.CascadeClassifier(r'C:\Users\msapp\Desktop\Winning hackathon\haarcascade_frontalface_default.xml')
SCREEN_SIZE = (1920, 1080)
fourcc = cv2.VideoWriter_fourcc(*"XVID")
cap = cv2.VideoCapture(0)

def record():
    #creates variables
    temp = []
    FPS = 1000
    duration = 10
    blackArray = []
    
    while(True):
        start = time.time()
        #takes picture of screen
        img = pyautogui.screenshot()
        frame = np.array(img)
        #convert colors from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #deletes the first image if necessary
        temp.append(frame)
        if(len(temp) > FPS * duration):
            temp.pop(0)
        
        #Face recording========================================================
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,     
            scaleFactor=1.2,
            minNeighbors=4,     
            minSize=(30, 30)
        )
        
        areas = []
        #draws box around the face and determines area to find the main (biggest) face if many are detected
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            areas.append(w*h)
                
        #gets the mouth region
        if(len(faces) > 0):
            #crop image
            mainFace = faces[areas.index(max(areas))]
            fullImage = Image.fromarray(img)
            cropped = fullImage.crop((x+(w/4), y+(h/1.75), x+w-(w/4), y+h))
            
            #convert back to array
            mouth = np.asarray(cropped)
            mouth = cv2.cvtColor(mouth, cv2.COLOR_BGR2GRAY)
            #Image.fromarray(mouth).show()
            
            #detect black pixels
            blackCount = 1;
            for i in range(len(mouth)):
                for a in range(len(mouth[0])):
                    if(mouth[i][a] < 25):
                        blackCount += 1
            #adds to an array with all the blackCounts from the last 30 seconds
            print(blackCount)
            if(len(blackArray) < 10):
                blackArray.append(blackCount)
                continue
            average = sum(blackArray)/len(blackArray)
            if(blackCount > average * 5):
                print('is pogging')
            else:
                print('isnt pogging')
                blackArray.append(blackCount)
                
            if(len(blackArray) > 300):
                blackArray.pop(0)
            
                    
        
        #shows face recording
        cv2.imshow('video', img)
    
        #find minimum FPS so the video isnt sped up
        end = time.time()
        if(1/(end-start) < FPS):
            FPS = 1/(end-start)
            
        #REPLACE WITH DA POG
        if keyboard.is_pressed('q'):
            vid = cv2.VideoWriter("output.mp4", fourcc, FPS, (SCREEN_SIZE))
            for frame in temp:
                vid.write(frame)
            vid.release()
            
        #REPLACE WITH CLICKING STOP BUTTON
        k = cv2.waitKey(30) & 0xff
        if k == 27: # press 'ESC' to quit
            cv2.destroyAllWindows()
            break
    

record()
    
