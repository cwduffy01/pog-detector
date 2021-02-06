from tkinter import * 
from tkinter.ttk import *
import cv2
from PIL import Image, ImageTk
from datetime import datetime

root = Tk()     # begins Tk application
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')    # video codec

class PogDetector:
    frame_rate = 0      # the frame rate of the webcam in fps
    cap_length = 0      # the length of the video in seconds
    recording = False   # if the gui is actively recording
    detecting = False   # if the pog is being detected
    frames = []         # collection of frames for pst cap_length seconds

    def __init__(self, frame_rate, cap_length):
        self.frame_rate = frame_rate
        self.cap_length = cap_length

        # create label object with image from camera stream
        self.panel = Label(root, image=self.capture_frame())
        self.panel.pack()

        # create button objects
        self.btn_start = Button(root, text="Start", command=self.toggle_start)
        self.btn_end = Button(root, text="Stop", command=self.toggle_end)
        self.btn_record = Button(root, text="Record", command=self.record)
        self.btn_start.pack()
        self.btn_end.pack()
        self.btn_record.pack()

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
            date = datetime.now()
            date_string = datetime.strftime(date, "pog-%d_%m_%y-%I_%M_%S_%p")
            out = cv2.VideoWriter(f'{date_string}.avi', fourcc, self.frame_rate, (640,480))
            for f in self.frames:
                out.write(f)     # write each frame to 
            out.release()        # release video writer object
    
    def save_frame(self, image):
        self.frames.append(image)
        # shorten frames to amount of frames in the videos
        if len(self.frames) > (int(self.frame_rate) * self.cap_length):
            self.frames.pop(0)
        print(len(self.frames))

pd = PogDetector(cap.get(cv2.CAP_PROP_FPS), 5)
while(True):
    img = pd.capture_frame()    # reset label image
    pd.panel["image"] = img
    root.update()           # update GUI

root.mainloop()     # run GUI

"""
TODO: Incorporate the following Widgets
    Display Logo
    Choose Directory Button
    Dark Theme
    Record Screen Toggle Button
"""