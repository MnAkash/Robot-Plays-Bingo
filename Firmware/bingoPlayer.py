# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 22:24:58 2022

@author: akash

Serial Communication with arduino
----------------------------------
1. For board number selection will send --> x,y
    Where x and y are coordinate of the number to pressed considering top left as 0,0 and bottom right as 4,4

2. Solenoid up   --> 'u'

3. Solenoid down --> 'd'


    

"""
print("Loading models...")
import os, time
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import cv2
import easyocr
import imutils
import numpy as np
from paddleocr import PaddleOCR
from threading import Thread
from calibration import getCalibationData
from Robot import robot
from cameraHandle import VideoStreamWidget

r = robot()
cameraFeed = VideoStreamWidget()#run separate camera thread

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

#reader = easyocr.Reader(['en'], gpu=False) # this needs to run only once to load the model into memory
reader = PaddleOCR(lang='en', show_log = False)

numberPos, box, currentNumPos, bonusButtons, bingoButton, rotation =getCalibationData()
 
numbers = np.array([['', '', '', '', ''],
                   ['', '', '', '', ''],
                   ['', '', 'None', '', ''],
                   ['', '', '', '', ''],
                   ['', '', '', '', '']])
numberPressed = np.zeros((5,5),np.uint8) #Store which number is pressed in boolean 5x5 matrix

#Since there is a logo at the middle of the board,
#consider that pressed where we already put "None" as number
numberPressed[2][2] = 1



template = cv2.imread("resources/go.png")
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)


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
        result = reader.ocr(image, cls=False)
        if len(result):
            text = result[0][1][0]
            text = text.replace("|", "1")
            text = text.replace(" ", "")
            if verbose:print(text)
        
        else:        
            image = cv2.resize(image, (100, 100), interpolation = cv2.INTER_AREA)
            result = reader.ocr(image, cls=False)
            
            
            if len(result):
                text = result[0][1][0]
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
            
            # zoom = int(box*0.1) #To remove 10% borders
            # finalFrame = finalFrame[zoom:-zoom, zoom:-zoom]
            
            text = getOcrResult(finalFrame, verbose)
            
            numbers[i][j] = text


def getColor(hist, verbose = False):    
    value = np.argmax(hist)
    if value == 0:
        #if zero has maximum occurance in histogram, look for 2nd best occurance
        hist = np.delete(hist, 0)
        value = np.argmax(hist)+1
        
        
    if value in range(1,24):
        if verbose:print("Red")
        return 'B'
    elif value in range(24,70):
        if verbose:print("Yellow")
        return 'G'
    elif value in range(70,92):
        if verbose:print("Green")
        return 'O'
    elif value in range(92,122):
        if verbose:print("Blue")
        return 'I'
    elif value in range(122,250):
        if verbose:print("Violet")
        return 'N'
    else:
        if verbose:print("None")
        return "None"
        
def getCurrentNumber(frame, verbose = False, showHistogram=False):
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
    
    
    
    # cv2.imshow("Image", finalFrame)
    # cv2.waitKey(1)
    hsvFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsvFrame],[0],None,[256],[0,256]) #get histogram of hue channel
    if showHistogram:
        from matplotlib import pyplot as plt
        plt.plot(hist, color='b')
        plt.title('Image Histogram For Blue Channel GFG')
        plt.show()
    letter = getColor(hist)
    
    
    #finalFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Current Number", finalFrame)
    cv2.waitKey(1)
    number = getOcrResult(finalFrame, verbose)
    
    
    if len(number)==1:
        if letter=='B':#Only B column has single digit numbers
            return number
        else:
            return 'None'
    else:
        return number


def getBonusButtons(frame, verbose = False):
    """
    

    Parameters
    ----------
    frame : numpy array of image
    verbose : bool, optional
        If true will print result and show detection image. Default is False.

    Returns
    -------
    result : list
        ['type', 'type'], type can be > 'g', 'Blank', 'G' (g for Gem, G for Guess)

    """
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
            result.append("g")
        elif value in range(108,120):
            if verbose:print("Blank")
            result.append("Blank")
        elif value in range(120,140):
            if verbose:print("Guess")
            result.append("G")
        else:
            print("None")
            
    return result

def getGuessNumbers(frame, verbose = False):
    x1 = numberPos[0][0][0] + int(box*0.5)
    y1 = numberPos[0][0][1] + int(box*2.5)
    frame1 = frame[y1:y1+box, x1:x1+box]
    
    x2 = numberPos[0][0][0] + int(box*2)
    y2 = numberPos[0][0][1] + int(box*0.8)
    frame2 = frame[y2:y2+box, x2:x2+box]
    
    x3 = numberPos[0][0][0] + int(box*3.5)
    y3 = numberPos[0][0][1] + int(box*2.5)
    frame3 = frame[y3:y3+box, x3:x3+box]
    
    x4 = numberPos[0][0][0] + int(box*2)
    y4 = numberPos[0][0][1] + int(box*4.2)
    frame4 = frame[y4:y4+box, x4:x4+box]
    
    
    if verbose:
        cv2.imshow("Image1", frame1)
        cv2.imshow("Image2", frame2)
        cv2.imshow("Image3", frame3)
        cv2.imshow("Image4", frame4)
        cv2.waitKey(1)
        
    P = getOcrResult(frame1, verbose)
    Q = getOcrResult(frame2, verbose)
    R = getOcrResult(frame3, verbose)
    S = getOcrResult(frame4, verbose)
    
    return P,Q,R,S

def checkBestNextNumber_withGiven(givenList):
    '''
    Bingo occurs when all numbers in a row/column has each number pressed 

    Parameters
    ----------
    givenList : list
        list of numbers to be checked for best next number to make a bingo

    Returns
    -------
    bestNumber : int
        Best number to push the board closer to make a bingo

    '''
    scores = []#store scores for each number being best next number to make a bingo
    for given in givenList:
        pos = np.where(numbers==given)
        if len(pos[0]):#if number available on list
            X, Y = pos[0][0], pos[1][0]
            if numberPressed[X][Y] == 0:#If not already pressed
                score = np.sum(numberPressed[X,:]) + np.sum(numberPressed[:,Y])
                scores.append(score)
            else:
                scores.append(0)
        else:
            scores.append(0)
    
    result = givenList[scores.index(max(scores))] #which max score in givenList is the final return result
    return result
   
def isBingo(frame, verbose=False):
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
    
def isStart(frame):
    templateThreshold = 0.5
    
    xmin = numberPos[0][0][0] + int(box*1.2)
    ymin = numberPos[0][0][1] + box
    xmax = xmin + int(box*2.4)
    ymax = ymin + int(box*1.5)
    finalFrame = frame[ymin:ymax, xmin:xmax]

    
    hsvFrame = cv2.cvtColor(finalFrame, cv2.COLOR_BGR2HSV)
    hueChannel = hsvFrame[:,:,0]
    
    #Yellow color has range of 25 to 60
    finalFrame = cv2.inRange(hueChannel, 25, 60)    
    
    cv2.imshow("Image", finalFrame)
    cv2.waitKey(1)
            
    result = cv2.matchTemplate(finalFrame,template,cv2.TM_CCOEFF_NORMED)[0][0]
    
    print(result)
    
    if templateThreshold < result:
        return True
    else:
        return False


def remainingTime(frame):
    '''
    Parameters
    ----------
    frame : numpy array of image
    verbose : bool, optional
    If true will print result and show detection image. Default is False.

    Returns
    -------
    None
    
    Updates
    -------
    global remaining_time : int/None
        remaining time in seconds. If cant detect will return none

    '''
    global remaining_time
    
    xmin = numberPos[0][0][0] + int(box*3.8)
    ymin = numberPos[0][0][1] - int(box*3.4)
    xmax = xmin + int(box*1.2)
    ymax = ymin + int(box*1)
    finalFrame = frame[ymin:ymax, xmin:xmax]

    # cv2.imshow("Time", finalFrame)
    # cv2.waitKey(1)
            
    number = getOcrResult(finalFrame, False)
    #number is in form --> "m:ss"
    
    if len(number)==4:#4 char in string
        try:
            minute = int(number[0])
            second = int(number[2:])
            remaining_time = minute*60 + second
            
        except:
            remaining_time = None
    else:
        remaining_time = None

  
def rotate_image(image, angle):
    if(angle<0):
        angle= 360+angle
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

#%%


#capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
while(True):
    frame = cameraFeed.frame
    frame = rotate_image(frame, rotation)#rotate image to allign screen
    if isStart(frame):
        cv2.destroyAllWindows()
        break
print("Game Start")


time.sleep(0.8)
frame = rotate_image(cameraFeed.frame, rotation)#rotate image to allign screen
# cv2.imshow("Image", frame)
# cv2.waitKey(1)
currentNum = getCurrentNumber(frame, verbose= True)
   
tic = time.time()
getBoardNumbers(frame, True)
print(time.time()-tic)


#start time keeping in seperate thread to not waste main loop time
remaining_time = 120
timeThread = Thread(target=remainingTime, args=(rotate_image(cameraFeed.frame, rotation), ))#feed rotation corrected frame
timeThread.daemon = True


while(True):
    timeThread.start() #update remaining time in separate thread
    
    frame = rotate_image(cameraFeed.frame, rotation)#rotate image to allign screen
    lastNumber = currentNum
    currentNum = getCurrentNumber(frame)
    
    if lastNumber != currentNum and currentNum.isnumeric():
        
        pos = np.where(numbers==currentNum)#if current number in board
        if len(pos[0]):
            X, Y = pos[0][0], pos[1][0]
            
            if numberPressed[X][Y] ==0:#if not already pressed           
                dataToSend = str(X) + ',' + str(Y)
                print(currentNum, end='')
                print(" at location > ",dataToSend)
                r.sendBoxCoords(X, Y)
                
                numberPressed[X][Y] = 1 #keep track which number is pressed
                
        else:
            print(currentNum)
            #print("Skiping ", currentNum)
            
            #==============Handle bonus buttons=========
            
            #Since cuurent number not in board, robot is free to check for bonus buttons
            bonusResult = getBonusButtons(frame)
            if bonusResult[0] != 'Blank':
                print(bonusResult[0])
                #command to press bonus button
                r.pressBonus1()
                


                frame = rotate_image(cameraFeed.frame, rotation)#rotate image to allign screen
                if bonusResult[0] == 'G':#if bonus is guess(Gimme More)
                    P,Q,R,S = getGuessNumbers(frame, verbose = True)
                    bestGuess = checkBestNextNumber_withGiven([P,Q,R,S])
                    print("Best Guess --> ", bestGuess)
                    #========Now press this best guessed number
                    pos = np.where(numbers==bestGuess)
                    if len(pos[0]):
                        X, Y = pos[0][0], pos[1][0]
                        
                        if numberPressed[X][Y] ==0:#if not already pressed
                            dataToSend = str(X) + ',' + str(Y)
                            print(bestGuess, end='')
                            print(" at location > ",dataToSend)
                            print("")#print extra line
                            r.sendBoxCoords(X, Y)
                            
                            numberPressed[X][Y] = 1 #keep track which number is pressed
                            
                          
                            
                          
                elif bonusResult[0] == 'g':#if bonus is gem(diamond)
                    #best guess from all the board numbers to make it close to bingo
                    bestGuess = checkBestNextNumber_withGiven(numbers.flatten())
                    print("Best Guess --> ", bestGuess)
                    #========Now press this best guessed number
                    pos = np.where(numbers==bestGuess)
                    if len(pos[0]):
                        X, Y = pos[0][0], pos[1][0]
                        
                        if numberPressed[X][Y] ==0:#if not already pressed
                            dataToSend = str(X) + ',' + str(Y)
                            print(bestGuess, end='')
                            print(" at location > ",dataToSend)
                            print("")#print extra line
                            r.sendBoxCoords(X, Y)
                            
                            numberPressed[X][Y] = 1 #keep track which number is pressed
                            
    
    #if time is less than 2 seconds check for bingo pressability
    print(remaining_time)
    if remaining_time !=None:
        if remaining_time <2:
            if isBingo(frame):
                print("Pressing Bingo")
                print("")
                r.pressBingo()
                #end the game
                break
            #end the game if not bingo too
            break
        
        
print("Game finished")
        
cameraFeed.close()


#%%
'''
while True:
    frame = cameraFeed.frame
    frame = rotate_image(frame, rotation)#rotate image to allign screen
    remaining = remainingTime(frame)
    print(remaining)
    #cv2.imshow("Image", frame)
    #cv2.waitKey(1)
'''