# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 22:24:58 2022

@author: akash
"""
import os, time
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import cv2
import easyocr
import imutils
import numpy as np
import serial
from calibration import getCalibationData
import warnings
warnings.filterwarnings("ignore", category=UserWarning) 

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




try:
    ser = serial.Serial(port='/dev/ttyUSB1',baudrate=9600)
    ser.open()
except Exception as e:
    print("Error openning serial port")
    #exit()

#%%
def getOcrResult(image, verbose=False):
    '''
    Parameters
    ----------
    image : numpy array
        webcam feed
    verbose : bool
        if true will print ocr result
    Returns
    -------
    text : string
        OCR result.

    '''
    try:
        result = reader.readtext(image)
        if len(result):
            text = result[0][1]
            text = text.replace("|", "1")
            text = text.replace(" ", "")
            if verbose:print(text)
            
        else:          
            image = cv2.resize(image, (100, 100), interpolation = cv2.INTER_AREA)
            result = reader.readtext(image)
            
            
            if len(result):
                text = result[0][1]
                text = text.replace("|", "1")
                text = text.replace(" ", "")
                if verbose:print(text)
                
            else:
                text = "None"
                if verbose:print("None")
                # cv2.imshow("Image", image)
                # cv2.waitKey(1500)
                
    except ValueError:
        text = "None"
        print('Error in OCR engine')
    
    return text
        
def getBoardNumbers(frame, verbose=False):
    '''
    Store all ocr result of number board in 'numbers' variable

    '''
    
    for i in range(5):
        for j in range(5):
            if i==2 and j==2:continue#Skip middle gem logo
            
            x = numberPos[i][j][0]
            y = numberPos[i][j][1]
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            finalFrame = frame_gray[y:y+box, x:x+box]
            
            zoom = int(box*0.1) #To remove 10% borders
            finalFrame = finalFrame[zoom:-zoom, zoom:-zoom]
            
            text = getOcrResult(finalFrame, verbose)
            
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
        
def getCurrentNumber(frame, verbose = False):
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
    
    #finalFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Current Number", finalFrame)
    cv2.waitKey(1)
    number = getOcrResult(finalFrame, verbose)
    
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

def isStart(frame):
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    xmin = numberPos[0][0][0] + int(box*1.2)
    ymin = numberPos[0][0][1] + box
    xmax = xmin + int(box*2.3)
    ymax = ymin + int(box*1.5)
    finalFrame = grey[ymin:ymax, xmin:xmax]

    '''
    hsvFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2HSV)
    hueChannel = hsvFrame[:,:,0]
    
    #Reed and yellow color has less than hue value 60
    _, thresh = cv2.threshold(hueChannel, 60, 255, cv2.THRESH_BINARY)
    

        
    kernel = np.ones((15,15),np.uint8)
    image = cv2.dilate(thresh,kernel,iterations = 1)
    '''
    cv2.imshow("Image", finalFrame)
    cv2.waitKey(1)
            
    
    result = reader.readtext(finalFrame, detail=False)
    if len(result):
        text = result[0]
        print(result)
        if text in ['GO', 'G0', 'C0', 'G', 'Q', 'C', '8','8o', '6', "8'"]:
            return True
        else:
            return False
    else:
        return False
#%%


capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
while(True):
    _, frame = capture.read()
    if isStart(frame):
        break
print("Game Start")

time.sleep(.5)
_, frame = capture.read()
currentNum = getCurrentNumber(frame, True)
   
tic = time.time()
getBoardNumbers(frame, True)
print(time.time()-tic)

while(True):
    pos = np.where(numbers==currentNum)
    if (len(pos[0])>0 and currentNum!='None'):
        X, Y = pos[0][0], pos[1][0]
        
        numberPressed[X][Y] = 1 #keep track which number is pressed
        
        dataToSend = str(X) + ',' + str(Y)
        print("Sent data > ",dataToSend)
        #ser.write(bytes(dataToSend, 'utf-8'))
        
    
    while(True):
        _, frame = capture.read()
        lastNumber = currentNum
        currentNum = getCurrentNumber(frame)
        if lastNumber != currentNum:
            print(currentNum)
            break
    
capture.release()
# bingo = isBingoActive(frame)
#bonus = getBonusButtons(frame)


'''
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
_, frame = capture.read()
eq=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
gauss = cv2.adaptiveThreshold(eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 45)
cv2.imshow("Image", gauss)

capture.release()
#cv2.destroyAllWindows()'''