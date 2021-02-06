from tkinter import *
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import os

root = Tk()     # begins Tk application
root.title("PogDetector™")
root.geometry("720x660")
root.resizable(False, False)
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')    # video codec

class PogDetector:
    frame_rate = 0      # the frame rate of the webcam in fps
    cap_length = 0      # the length of the video in seconds
    recording = False   # if the gui is actively recording
    detecting = False   # if the pog is being detected
    dark_mode = False   # if dark mode is enabled
    frames = []         # collection of frames for pst cap_length seconds
    logo = ImageTk.PhotoImage(Image.open("light_logo.png"))

    def __init__(self, frame_rate, cap_length):
        self.frame_rate = frame_rate
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

        if self.detecting:  # save cv2 image to frames list
            self.save_frame(frame)

        return img
    
    def toggle_start(self):
        self.detecting = True

    def toggle_end(self):
        self.detecting = False
        self.frames.clear()

    def record(self):
        if self.detecting:
            if "clips" not in os.listdir():
                os.mkdir("clips")

            date = datetime.now()
            date_string = datetime.strftime(date, "pog-%d_%m_%y-%I_%M_%S_%p")
            out = cv2.VideoWriter(f"clips/{date_string}.avi", fourcc, self.frame_rate, (640,480))
            for f in self.frames:
                out.write(f)     # write each frame to 
            out.release()        # release video writer object
    
    def save_frame(self, image):
        self.frames.append(image)
        # shorten frames to amount of frames in the videos
        if len(self.frames) > (int(self.frame_rate) * self.cap_length):
            self.frames.pop(0)

pd = PogDetector(cap.get(cv2.CAP_PROP_FPS), 5)
while(True):
    img = pd.capture_frame()    # reset label image
    pd.camera_panel["image"] = img
    root.update()           # update GUI

root.mainloop()     # run GUI

"""
TODO: Extra Features
    Choose Directory Button
    Dark Theme
    Record Screen Toggle Button
"""