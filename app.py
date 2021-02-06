from tkinter import * 
from tkinter.ttk import *
import cv2
from PIL import Image, ImageTk

root = Tk()     # begins Tk application
cap = cv2.VideoCapture(0)

class PogDetector:
    frame_rate = 0      # the frame rate of the webcam in fps
    cap_length = 0      # the length of the video in seconds
    recording = False   # if the gui is actively recording
    frames = []         # collection of frames for pst cap_length seconds

    def __init__(self, frame_rate, cap_length):
        self.frame_rate = frame_rate
        self.cap_length = cap_length

        # create label object with image from camera stream
        self.panel = Label(root, image=self.capture_frame())
        self.panel.pack()

        # create button objects
        self.btn_start = Button(root, text="Record", command=self.toggle_record)
        self.btn_start.pack()

    def capture_frame(self):
        ret, frame = cap.read()                 # read frame from webcam
        image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert to RGB color scheme
        image_pil = Image.fromarray(image_cv2)  # convert to PIL image
        img = ImageTk.PhotoImage(image_pil)     # convert to Tkinter image

        if self.recording:  # save cv2 image to frames list
            self.save_frame(frame)

        return img

    def toggle_record(self):
        if self.recording:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')    # video codec
            out = cv2.VideoWriter('output.avi', fourcc, self.frame_rate, (640,480))
            for f in self.frames:
                out.write(f)     # write each frame to 
            out.release()        # release video writer object
            self.frames.clear()  # reset frames list
            
        self.recording = not self.recording
    
    def save_frame(self, image):
        self.frames.append(image)
        # shorten frames to amount of frames in the videos
        if len(self.frames) > (int(self.frame_rate) * self.cap_length):
            self.frames.pop(0)

pd = PogDetector(cap.get(cv2.CAP_PROP_FPS), 5)
while(True):
    img = pd.capture_frame()    # reset label image
    pd.panel["image"] = img
    root.update()           # update GUI

root.mainloop()     # run GUI

"""
TODO: Incorporate the following Widgets
    - Start/Stop Button: Button
    - File Location: Entry
    - Directories: Scrollbar/Spinbox?? Menu??
    - Dark mode
"""