from tkinter import *
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import os
import numpy as np

root = Tk()     # begins Tk application
root.title("PogDetector™")
root.geometry("720x660")
root.resizable(False, False)

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')    # video codec
faceCascade = cv2.CascadeClassifier(r'haarcascade_frontalface_default.xml')
detector = cv2.SimpleBlobDetector_create()

class PogDetector:
    frame_rate = 0      # the frame rate of the webcam in fps
    cap_length = 0      # the length of the video in seconds
    recording = False   # if the gui is actively recording
    detecting = False   # if the pog is being detected
    saving = False
    frames = []         # collection of frames for pst cap_length seconds
    logo = ImageTk.PhotoImage(Image.open("light_logo.png"))
    black_values = []
    pogs = []

    def __init__(self, cap, cap_length):
        self.frame_rate = cap.get(cv2.CAP_PROP_FPS)
        self.frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print(self.frame_size)
        self.cap_length = cap_length

        # create label object with image from camera stream
        self.logo_panel = Label(root, image=self.logo)
        self.camera_panel = Label(root, image=self.capture_frame())
        self.logo_panel.place(anchor=N, y=15, x=360)
        self.camera_panel.place(anchor=N, y=100, x=360)

        # create button objects
        play = ImageTk.PhotoImage(Image.open("start.png"))
        self.btn_start = Button(root, image=play, command=self.toggle_start, height=35, width=35)
        self.btn_start.image = play

        stop = ImageTk.PhotoImage(Image.open("stop.png"))
        self.btn_end = Button(root, image=stop, command=self.toggle_end, height=35, width=35)
        self.btn_end.image = stop

        record = ImageTk.PhotoImage(Image.open("record.png"))
        self.btn_record = Button(root, image=record, command=self.record, height=35, width=35)
        self.btn_record.image = record

        self.btn_start.place(anchor=N, y=600, x=360)
        self.btn_end.place(anchor=N, y=600, x=410)
        self.btn_record.place(anchor=N, y=600, x=310)

    def capture_frame(self):
        ret, frame = cap.read()                 # read frame from webcam
        image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert to RGB color scheme
        image_pil = Image.fromarray(image_cv2)  # convert to PIL image
        img = ImageTk.PhotoImage(image_pil)     # convert to Tkinter image

        no_box = frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,     
            scaleFactor=1.2,
            minNeighbors=4,     
            minSize=(30, 30)
        )

        areas = []
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            areas.append(w*h)

        pog = False
        if self.detecting:
            self.save_frame(no_box)
            if len(faces) > 0:
                main_face = faces[areas.index(max(areas))]
                cropped = image_pil.crop((x+(w/4), y+(h/1.75), x+w-(w/4), y+h))
                mouth = np.asarray(cropped)
                mouth = cv2.cvtColor(mouth, cv2.COLOR_BGR2GRAY)
                pog = self.check_pog(mouth)
        if self.saving:
            self.save_frame(no_box)
            self.pogs.clear()
            if len(self.frames) >= ((self.cap_length + 5) * self.frame_rate) - 10:
                self.record()

        try:
            (x, y, w, h) = faces[areas.index(max(areas))]
            if pog:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)
        except:
            pass

        image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert to RGB color scheme
        image_pil = Image.fromarray(image_cv2)  # convert to PIL image
        img = ImageTk.PhotoImage(image_pil)     # convert to Tkinter image

        return img

    def check_pog(self, mouth):
        keypoints = detector.detect(mouth)
        pog = False
        if keypoints:
            for kp in keypoints:
                if 30 <= kp.size <= 50:
                    pog = True
                    break

        self.pogs.append(pog)
        if len(self.pogs) > 10:
            self.pogs.pop(0)

        return pog
    
    def toggle_start(self):
        self.detecting = True

    def toggle_end(self):
        self.detecting = False
        self.black_values = []
        self.frames.clear()

    def record(self):
        self.saving = False

        if "clips" not in os.listdir():
            os.mkdir("clips")

        date = datetime.now()
        date_string = datetime.strftime(date, "pog-%d_%m_%y-%I_%M_%S_%p")
        out = cv2.VideoWriter(f"clips/{date_string}.avi", fourcc, self.frame_rate, self.frame_size)
        for f in self.frames:
            out.write(f)     # write each frame to 
        out.release()        # release video writer object

        self.frames.clear()
        self.detecting = True
    
    def save(self):
        self.saving = True
        self.detecting = False
    
    def save_frame(self, image):
        self.frames.append(image)
        # shorten frames to amount of frames in the videos
        if len(self.frames) > (self.frame_rate) * self.cap_length and not self.saving:
            self.frames.pop(0)

pd = PogDetector(cap, 5)

while(True):
    img = pd.capture_frame()    # reset label image
    pd.camera_panel["image"] = img

    if all(pd.pogs) and pd.pogs:
        pd.save()
        print("Saving...")

    root.update()           # update GUI

root.mainloop()     # run GUI

"""
TODO: Extra Features
    Display when button is pressed/not pressed? Display when recording? Prevent buttons from being pressed?
    Display when a person is pogging or not

    Dark Theme
    Enable/Disable Music overlay
    Enable/Disable Screen Record
    Where the webcam feed is placed (which corner)
    About Menu (What does each icon mean?)
"""

"""
TODO: SATURDAY
    Merging the files app.py and hackathon.py
    Record audio and add it to video
        Otherwise, add music to the background of the video
            Epic EDM song (10 seconds before pog, 5 seconds after)
    Play sound when pog detected
    Save video like lets play
    Add more GUI features
    Format the GitHub
"""