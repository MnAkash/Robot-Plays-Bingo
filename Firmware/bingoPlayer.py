# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 22:24:58 2022

@author: akash
"""

import cv2
import pytesseract
import imutils
from calibration import calibrate

# Connects pytesseract(wrapper) to the trained tesseract module
pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\akash\\AppData\\Local\\Tesseract-OCR\\tesseract.exe'


a, b, box= calibrate()


capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:

    _, frame = capture.read()
    
    # B, G, R channel splitting
    # blue, green, red = cv2.split(frame)

    # for i in range(5):
    #     for j in range(5):
    #         xmin = a[i][j].x
    #         ymin = a[i][j].y
    #         cv2.circle(frame,(xmin,ymin),5,(0,0,255),3)
    
    #frame = imutils.resize(image=frame, width=500)
    
    #frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    x = a[0][0].x
    y = a[0][0].y
    
    
    finalFrame = frame_rgb[y:y+box, x:x+box]
    #cv2.imshow('frame', frame_gray)

    try:
        print("Detecting")
        text = pytesseract.image_to_string(finalFrame)
        print(text)
    except ValueError:
        print('except')
    cv2.imshow('Frame', finalFrame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



capture.release()
cv2.destroyAllWindows()