import cv2
import numpy as np
import pyautogui
import keyboard
import time
from PIL import Image

faceCascade = cv2.CascadeClassifier(r'C:\Users\Scot\Desktop\Test\haarcascade_frontalface_default.xml')
SCREEN_SIZE = (1920, 1080)
fourcc = cv2.VideoWriter_fourcc(*"XVID")
cap = cv2.VideoCapture(0)

def record():
    #creates variables
    temp = []
    FPS = 1000
    duration = 15
    blackArray = []
    pogCount = 0
    
    readyToRecord = False
    stopRecord = 0
    framesAfterPog = 0
    
    while(True):
        start = time.time()
        
        #takes picture of screen in Image type, converts the colors, and turns it back into an image
        frame = pyautogui.screenshot()
        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePic = Image.fromarray(frame)
        
        #takes picture of face cam as np array and converts to image
        ret, img = cap.read()
        imagePic = Image.fromarray(img)
        imagePic = imagePic.resize((int(len(img[0])/2), int(len(img)/2)))
        
        #puts face cam in the top left of the screen cap
        framePic.paste(imagePic)
        overlaid = np.asarray(framePic)
        
        #adds the new overlaid frame and deletes the first image if necessary
        temp.append(overlaid)
        if(len(temp) > FPS * duration):
            temp.pop(0)
        
        #Face recognition==========================================================================
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
            
            #detect black pixels
            ret, black = cv2.threshold(mouth, 25, 255, cv2.THRESH_BINARY_INV)
            cv2.imshow("mouth", black)
            blackCount = np.sum(black == 255)
                        
            #makes sure there are 10 sample frames to start with
            if(len(blackArray) < 10):
                blackArray.append(blackCount)
                continue
            
            #finds the average from the blackCount list, if the current
            #blackCount is 3x bigger than the average, it assumes they are pogging
            isPogging = False
            average = sum(blackArray)/len(blackArray)
            if(blackCount > average * 3):
                #print('is pogging')
                isPogging = True
            else:
                #print('isnt pogging')
                isPogging = False
                blackArray.append(blackCount)
            if(len(blackArray) > 300):
                blackArray.pop(0)
            
            #counts the number of consecutive frames the user is pogging
            if(isPogging):
                pogCount += 1
            else:
                pogCount = 0
                       
        #shows face recording
        cv2.imshow('video', img)
    
        #find minimum FPS so the video isnt sped up
        end = time.time()
        if(1/(end-start) < FPS):
            FPS = 1/(end-start)
            
        #if the past 10 recorded frames have been pogging, checks that its ready
        if(pogCount > 10):     
            readyToRecord = True
        
        #continues to record for an aditional 5 seconds after the pog has been first detected
        if(readyToRecord and framesAfterPog < FPS*5 - 10):
            framesAfterPog += 1
        #if it has been 5 seconds since the intital pog, it saves the video
        elif(readyToRecord):
            readyToRecord = False
            framesAfterPog = 0
            vid = cv2.VideoWriter("output.mp4", fourcc, FPS, (SCREEN_SIZE))
            for frame in temp:
                vid.write(frame)
            print('Releasing video')
            vid.release()
            
        #REPLACE WITH CLICKING STOP BUTTON
        k = cv2.waitKey(30) & 0xff
        if k == 27: # press 'ESC' to quit
            cv2.destroyAllWindows()
            break
    

record()

