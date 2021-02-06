from tkinter import * 
from tkinter.ttk import *
import cv2
from PIL import Image, ImageTk

root = Tk()     # begins Tk application

cap = cv2.VideoCapture(0)

class PogDetector:
    def __init__(self):
        self.panel = Label(root, image=self.capture_frame())  # create label object with image from camera stream
        self.panel.pack()

        self.btn_start = Button(root, text="Record", command=self.pressed)
        self.btn_start.pack()
        
        self.recording = False

    def capture_frame(self):
        ret, frame = cap.read()
        image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_cv2)
        img = ImageTk.PhotoImage(image_pil)
        return img

    def pressed(self):
        self.recording = not self.recording
        print(self.recording)

pd = PogDetector()
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