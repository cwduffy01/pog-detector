from tkinter import *
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import os
import numpy as np
import pyautogui
import moviepy.editor as mpe
import time

root = Tk()     # begins Tk application
root.title("PogDetector™")
root.geometry("720x660")
root.iconbitmap("assets/pog.ico")
root.resizable(False, False)

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*"XVID")
faceCascade = cv2.CascadeClassifier(r'assets/haarcascade_frontalface_default.xml')
detector = cv2.SimpleBlobDetector_create()

class PogDetector:
    frame_rate = 0      # the frame rate of the webcam in fps
    cap_length = 0      # the length of the video in seconds
    recording = False   # if the gui is actively recording
    detecting = False   # if the pog is being detected
    saving = False
    frames = []         # collection of frames for past cap_length seconds
    logo = ImageTk.PhotoImage(Image.open("assets/logo.png"))
    pogs = []
    start_times = []
    pog_start = 0

    def __init__(self, cap, cap_length):
        self.frame_rate = cap.get(cv2.CAP_PROP_FPS)
        self.frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.cap_length = cap_length

        # create label object with image from camera stream
        self.logo_panel = Label(root, image=self.logo)
        self.camera_panel = Label(root, image=self.capture_frame())
        self.logo_panel.place(anchor=N, y=15, x=360)
        self.camera_panel.place(anchor=N, y=100, x=360)

        # create button objects
        play = ImageTk.PhotoImage(Image.open("assets/start.png"))
        self.btn_start = Button(root, image=play, command=self.toggle_start, height=35, width=35)
        self.btn_start.image = play

        stop = ImageTk.PhotoImage(Image.open("assets/stop.png"))
        self.btn_end = Button(root, image=stop, command=self.toggle_end, height=35, width=35)
        self.btn_end.image = stop

        self.btn_start.place(anchor=N, y=600, x=335)
        self.btn_end.place(anchor=N, y=600, x=385)

    def capture_frame(self):
        self.start_times.append(time.time())

        ret, frame = cap.read()                 # read frame from webcam
        image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert to RGB color scheme
        image_pil = Image.fromarray(image_cv2)  # convert to PIL image
        img = ImageTk.PhotoImage(image_pil)     # convert to Tkinter image

        #takes picture of screen in Image type, converts the colors, and turns it back into an image
        ss = pyautogui.screenshot()
        ss = np.array(ss)
        ss = cv2.cvtColor(ss, cv2.COLOR_BGR2RGB)
        ss_pil = Image.fromarray(ss)

        frame_pil = Image.fromarray(frame)
        frame_pil = frame_pil.resize((int(len(frame[0])/2), int(len(frame)/2)))

        ss_pil.paste(frame_pil)
        overlay = np.asarray(ss_pil)

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

        if self.detecting or self.saving:
            self.save_frame(overlay)

        pog = False
        if self.detecting:
            if len(faces) > 0:
                main_face = faces[areas.index(max(areas))]
                cropped = image_pil.crop((x+(w/4), y+(h/1.75), x+w-(w/4), y+h))
                mouth = np.asarray(cropped)
                mouth = cv2.cvtColor(mouth, cv2.COLOR_BGR2GRAY)
                pog = self.check_pog(mouth)

                (x, y, w, h) = main_face
                if pog:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), 2)
                else:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)
        if self.saving:
            self.pogs.clear()
            if len(self.frames) >= 100:
                self.record()

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
        self.btn_start.config(relief="sunken")

    def toggle_end(self):
        self.detecting = False
        self.black_values = []
        self.frames.clear()
        self.btn_start.config(relief="raised")

    def record(self):
        self.saving = False

        if "clips" not in os.listdir():
            os.mkdir("clips")

        fps = len(self.frames) / (time.time() - self.start_times[0])

        date = datetime.now()
        date_string = datetime.strftime(date, "pog-%d_%m_%y-%I_%M_%S_%p")
        out = cv2.VideoWriter(f"vid.avi", fourcc, fps, (1920, 1080))
        for f in self.frames:
            out.write(f)     # write each frame to 
        out.release()        # release video writer object

        vid = mpe.VideoFileClip("vid.avi")
        vid = vid.subclip(self.pog_start - self.start_times[0] - 10 - 1.5, self.pog_start - self.start_times[0] + 5 - 1.5)
        final_vid = vid.set_audio(mpe.AudioFileClip("assets/pog_music.mp3"))
        final_vid.write_videofile(f"clips/{date_string}.mp4", fps=fps, codec="libx264")
        os.remove("vid.avi")
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
            self.start_times.pop(0)

pd = PogDetector(cap, 10)

while(True):
    img = pd.capture_frame()    # reset label image
    pd.camera_panel["image"] = img

    if all(pd.pogs) and pd.pogs:
        pd.save()
        print("Saving...")
        pd.pog_start = time.time()

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
    Format the GitHub
        requirements.txt
"""