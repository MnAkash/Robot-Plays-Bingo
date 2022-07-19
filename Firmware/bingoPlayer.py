# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 22:24:58 2022

@author: akash
"""
import os, time
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import cv2
import pytesseract
import easyocr
import imutils
import numpy as np
from calibration import getCalibationData


pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\akash\\AppData\\Local\\Tesseract-OCR\\tesseract.exe'

reader = easyocr.Reader(['en'], gpu=False) # this needs to run only once to load the model into memory

numberPos, box, currentNumPos, bonusButtons, bingoButton = getCalibationData()
   
numbers = np.array([['', '', '', '', ''],
                   ['', '', '', '', ''],
                   ['', '', 'None', '', ''],
                   ['', '', '', '', ''],
                   ['', '', '', '', '']])
numberPressed = np.zeros((5,5),np.uint8) #Store which number is pressed in boolean 5x5 matrix

#Since there is a logo at the middle of the board,
#consider that pressed where we already put "None" as number
numberPressed[2][2] = 1


#%%
def getOcrResult(image):
    '''
    Parameters
    ----------
    image : numpy array
        webcam feed

    Returns
    -------
    text : string
        OCR result.

    '''
    try:
        result = reader.readtext(image)
        if len(result):
            text = result[0][1]
            text = text.replace(" ", "")
            print(text)
            
        else:          
            #image = image[3:-3, 3:-3] #crop edge
            
            
            
            # sharp = np.array([[0, -1, 0],
            #            [-1, 5,-1],
            #            [0, -1, 0]])
            # image = cv2.filter2D(src=image, ddepth=-1, kernel=sharp)
            
            '''
            ret, image = cv2.threshold(image, 155, 255, cv2.THRESH_BINARY)
            
            image = cv2.blur(image,(2,2))#Image blurring
            
            
            kernel = np.ones((2,2),np.uint8)
            image = cv2.dilate(image,kernel,iterations = 1)
            
            ret, image = cv2.threshold(image, 140, 255, cv2.THRESH_BINARY)
            '''
            image = cv2.resize(image, (90, 90), interpolation = cv2.INTER_AREA)
            print("2nd turn: ", end=' ')
            #print(pytesseract.image_to_string(image))
            
            result = reader.readtext(image)
            
            
            if len(result):
                text = result[0][1]
                text = text.replace(" ", "")
                print(text)
                cv2.imshow('Frame', image)
                cv2.waitKey(1500)
                
            else:
                text = "None"
                print("None")
                cv2.imshow('Frame', image)
                cv2.waitKey(1500)
                
    except ValueError:
        text = "None"
        print('except')
    
    return text
        
def getBoardNumbers(frame):
    '''
    Store all ocr result of number board in 'numbers' variable

    '''
    
    for i in range(5):
        for j in range(5):
            if i==2 and j==2:continue#Skip middle gem logo
            
            x = numberPos[i][j][0]
            y = numberPos[i][j][1]
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #ret, thresh = cv2.threshold(frame_gray, 100, 255, cv2.THRESH_BINARY)
            #kernel = np.ones((5,5),np.uint8)
            #dst = cv2.erode(thresh,kernel,iterations = 1)
            
            
            finalFrame = frame_gray[y:y+box, x:x+box]
            
            zoom = int(box*0.1) #To remove 10% borders
            finalFrame = finalFrame[zoom:-zoom, zoom:-zoom]
            
    
            text = getOcrResult(finalFrame)
            
            numbers[i][j] = text

def getColor(hist):    
    value = np.argmax(hist)
    if value == 0:
        #if zero has maximum occurance in histogram, look for 2nd best occurance
        hist = np.delete(hist, 0)
        value = np.argmax(hist)+1
        
        
    if value in range(1,24):
        print("Red")
        return 'B'
    elif value in range(24,70):
        print("Yellow")
        return 'G'
    elif value in range(70,92):
        print("Green")
        return 'O'
    elif value in range(92,122):
        print("Blue")
        return 'I'
    elif value in range(122,250):
        print("Violet")
        return 'N'
    else:
        print("None")
        return "None"
        
def getCurrentNumber(frame, showHistogram = False):
    """
    

    Parameters
    ----------
    frame : numpy array
        Camera feed of full game screen.

    Returns
    -------
    number : String
        current number.

    """
    xmin = currentNumPos[0]
    ymin = currentNumPos[1]
    xmax = currentNumPos[2]
    ymax = currentNumPos[3]
    finalFrame = frame[ymin:ymax, xmin:xmax]
    
    
    '''
    cv2.imshow("Image", finalFrame)
    cv2.waitKey(1)
    hsvFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2HSV)
    
    hist = cv2.calcHist([hsvFrame],[0],None,[256],[0,256]) #get histogram of hue channel
    
    if showHistogram:
        from matplotlib import pyplot as plt
        plt.plot(hist, color='b')
        plt.title('Image Histogram For Blue Channel GFG')
        plt.show()

    letter = getColor(hist)
    '''
    
    #finalFrame = finalFrame[10:, :]
    finalFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2GRAY)
    number = getOcrResult(finalFrame)
    
    return number

def isBingoActive(frame, verbose=False):
    xmin = bingoButton[0]
    ymin = bingoButton[1]
    xmax = bingoButton[2]
    ymax = bingoButton[3]
    finalFrame = frame[ymin:ymax, xmin:xmax]
    
    if verbose:
        cv2.imshow("Image", finalFrame)
        cv2.waitKey(1)
        
    hsvFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsvFrame],[0],None,[256],[0,256]) #get histogram of hue channel
    value = np.argmax(hist)
    
    if value < 135:
        if verbose:print("Bingo Inactive")
        return False
    else:
        if verbose:print("Bingo Aactive")
        return True

def getBonusButtons(frame, verbose = False):
    result = []
    for i in range(2):
        xmin = bonusButtons[i][0]
        ymin = bonusButtons[i][1]
        xmax = bonusButtons[i][2]
        ymax = bonusButtons[i][3]
        finalFrame = frame[ymin:ymax, xmin:xmax]
        zoom = int((xmax-xmin)/5)
        finalFrame = finalFrame[zoom:-zoom, zoom:-zoom]
        if verbose:
            cv2.imshow("Image", finalFrame)
            cv2.waitKey(1)
            
        hsvFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsvFrame],[0],None,[256],[0,256]) #get histogram of hue channel
        
        if verbose:        
            from matplotlib import pyplot as plt
            plt.plot(hist, color='b')
            plt.title('Image Histogram For Blue Channel GFG')
            plt.show()
        
        value = np.argmax(hist)
        if value in range(90,108):
            if verbose:print("Gem")
            result.append("Gem")
        elif value in range(108,120):
            if verbose:print("Blank")
            result.append("Blank")
        elif value in range(120,140):
            if verbose:print("Guess")
            result.append("Guess")
        else:
            print("None")
            
    return result


capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
_, frame = capture.read()
getBoardNumbers(frame)
currentrNum = getCurrentNumber(frame)
# bingo = isBingoActive(frame)
#bonus = getBonusButtons(frame)


capture.release()
#cv2.destroyAllWindows()

#%%

#text issue
# frame = cv2.imread("1.png")
'''
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
_, frame = capture.read()
# denoised = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 15)



x = numberPos[3][0][0]
y = numberPos[3][0][1]

frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#ret, thresh = cv2.threshold(frame_gray, 100, 255, cv2.THRESH_BINARY)
#kernel = np.ones((5,5),np.uint8)
#dst = cv2.erode(thresh,kernel,iterations = 1)


finalFrame = frame_gray[y:y+box, x:x+box]

finalFrame = finalFrame[3:-3, 3:-3]
resize = cv2.resize(finalFrame, (400, 400), interpolation = cv2.INTER_AREA)

ret, dst = cv2.threshold(resize, 150, 255, cv2.THRESH_BINARY)


  
# resize image





# kernel = np.ones((1,1),np.uint8)
# # dst = cv2.erode(thresh,kernel,iterations = 1)
# dst = cv2.dilate(grey,kernel,iterations = 1)


pytesseract.image_to_string(dst)
reader.readtext(dst)
reader.readtext(finalFrame)


cv2.imshow("Image", dst)
cv2.imshow("Image", finalFrame)


reader.readtext(dst)
'''

