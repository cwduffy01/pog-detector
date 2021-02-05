from tkinter import * 
from tkinter.ttk import *
import cv2
from PIL import Image, ImageTk
    
root = Tk()     # begins Tk application

cap = cv2.VideoCapture(0)

ret, frame = cap.read()     # frame: the actual frame read from the video feed
image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert from BGR to RGB for PIL
image_pil = Image.fromarray(image_cv2)  # convert image to PIL Image
img = ImageTk.PhotoImage(image_pil)     # convert image to Tkinter Image

panel = Label(root, image=img)  # create label object with image from camera stream
panel.pack()

while(True):
    # capture new frame
    ret, frame = cap.read()
    image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_cv2)
    img = ImageTk.PhotoImage(image_pil)

    panel["image"] = img    # reset label image
    root.update()           # update GUI

root.mainloop()     # run GUI


"""
TODO: Incorporate the following Widgets
    - Start/Stop Button: Button

    - File Location: Entry
    - Directories: Scrollbar/Spinbox?? Menu??

    - Dark mode
"""