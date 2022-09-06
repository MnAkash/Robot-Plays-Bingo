# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pandas as pd
import time, math
import yaml
from paddleocr import PaddleOCR
from Robot import robot

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# r = robot()
# time.sleep(2)
# r.goHome()



class Point:
    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.text = "None"


def getContours(img, imgContour):
    squares = []
    circles = []
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        #print(area)
        if area>500:
            #cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt,True)
            #print(peri)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
            #print(len(approx))
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)

            if objCor ==3: objectType ="Tri"
            elif objCor == 4:
                aspRatio = w/float(h)
                if aspRatio >0.9 and aspRatio <1.1: objectType= "Square"
                else:objectType="Rectangle"
            elif objCor>4: objectType= "Circle"
            else:objectType="None"

            
            if objectType == "Square":
                squares.append( (x,y,w,h) )
                
                cv2.rectangle(imgContour,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.putText(imgContour,objectType,
                            (x+(w//2)-10,y+(h//2)-10),cv2.FONT_HERSHEY_COMPLEX,0.7,
                            (0,0,0),2)
    
    cv2.imshow("Image", imgContour)
    return squares, circles


def rotate_image(image, angle):
    if(angle<0):
        angle= 360+angle
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def getRotation(frame):
    '''
    Using Top left '5' and Bottom Left '70' to get camera rotation
    
    input : camera frame
    output : rotation in degree to align mobile straight
    '''
    topLeft = '4'
    topRight = '61'
    print("Extracting camera rotation")
    reader = PaddleOCR(lang='en', show_log = False)
    result = reader.ocr(frame, cls=False)
       
    
    Xcoord = [None, None] #1st loc for topLeft 2nd for topRight
    Ycoord = [None, None]
    
    for res in result:
        if res[1][0] == topLeft: 
            Xcoord[0] = res[0][0][0]
            Ycoord[0] = res[0][0][1]
        
        elif res[1][0] == topRight:
            Xcoord[1] = res[0][0][0]
            Ycoord[1] = res[0][0][1]
    
    try:
        #Considering opencv y axis starts from top left corner
        rotation = math.atan2(Ycoord[0]-Ycoord[1], Xcoord[1]-Xcoord[0])
        rotation = -math.degrees(rotation)
        return rotation
    except:
        raise TypeError("Try alligning the screen")

def calibrate():
    '''
    Calibrate camera with game initial display
    
    parameters: None
    return  : allPoints     : [5][5] points with 'x','y' and 'text' of 25 square boxs
            : box           : sides of squares
            : currentNumPos : [xmin, ymin, xmax, ymax]
            : bonusButtons  : [xmin1, ymin1, xmax1, ymax1], [xmin2, ymin2, xmax2, ymax2]
            : bingoButtton  : [xmin, ymin, xmax, ymax]
    '''
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    allSquares = []
    

    while True:
        #Wait before 'c' button pressed
        _, img = capture.read()
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            #cv2.destroyAllWindows()
            break
        
    rotation = getRotation(img)
    print("Camera Rotation :", rotation)
    print("Calibrating...")

    start = time.time()  
    while (time.time()-start) < 3:
    
        _, img = capture.read()
        img = rotate_image(img, rotation)#rotate image to allign screen
        
        imgContour = img.copy()
        
        imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(7,7),1)
        imgCanny = cv2.Canny(imgBlur,50,50)
        
        
        squares, circles = getContours(imgCanny, imgContour)
        
        allSquares += squares       
    
        cv2.waitKey(1)
        
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     #time.sleep(5)
        #     break
    
    capture.release()
    cv2.destroyAllWindows()
    
       
    
    allSquares = list(set(allSquares))
    allSquaresDF = pd.DataFrame.from_records(allSquares, columns =['X', 'Y', 'W', 'H'])
    xmin, ymin, wmin, hmin = allSquaresDF.min()
    xmax, ymax, wmax, hmax = allSquaresDF.max()
    
    box = int((xmax - xmin)/4)
    
    unitVector = np.array([int((xmax - xmin)/4), int((ymax - ymin)/4)])
    initialPos = np.array([xmin, ymin])
    
    #=====================================Calculating random number appearing location
    
    #3.85, -1.85 is the relative loaction of random number appearing from initial position
    currentNumPos =  unitVector*np.array([3.75, -1.8]) + initialPos
    #append end point to currentNumPos array
    currentNumPos = np.append(currentNumPos, currentNumPos+np.array([box*1.3, box*1.35]))
    #Convert everything to int
    currentNumPos = currentNumPos.astype(int).tolist()
    
    
    #=====================================Calculating two bonus buttons location
    
    #0.45, 5.8 is the relative loaction of 1st bonus button from initial position
    bonusButton1 =  unitVector*np.array([0.45, 5.5]) + initialPos
    #append end point of 1st bonus button to bonusButton1 array
    bonusButton1 = np.append(bonusButton1, bonusButton1+np.array([box*0.7, box*0.7]))
    
    #1.5, 5.8 is the relative loaction of 2nd bonus button from initial position
    bonusButton2 =  unitVector*np.array([1.5, 5.5]) + initialPos
    #append end point of 2nd bonus button to bonusButton1 array
    bonusButton2 = np.append(bonusButton2, bonusButton2+np.array([box*0.7, box*0.7]))
    
    #Append both both button location in one 2d array
    bonusButtons = np.append(bonusButton1, bonusButton2).reshape(2,4)
    
    #Convert everything to int
    bonusButtons = bonusButtons.astype(int).tolist()
    
    
    
    #=====================================Calculating bingo button location
    
    #2.9, 5.6 is the relative loaction of bingo button from initial position
    bingoButtton =  unitVector*np.array([2.9, 5.6]) + initialPos
    #append end point to bingoButtton array
    bingoButtton = np.append(bingoButtton, bingoButtton+np.array([box*1.9, box*0.8]))
    #Convert everything to int
    bingoButtton = bingoButtton.astype(int).tolist()
    
    #test scraped location
    # xmin = bingoButtton[0]
    # ymin = bingoButtton[1]
    # xmax = bingoButtton[2]
    # ymax = bingoButtton[3]
    # finalFrame = img[ymin:ymax, xmin:xmax]
    # cv2.imshow("Image", finalFrame)
    
    
    #Store all number box positions in numberPos variable
    numberPos = []
    for i in range(5):
        tempList = []
        for j in range(5):
            tempList.append((xmin+j*box, ymin+i*box))
            cv2.circle(img,(xmin+i*box,ymin+j*box),5,(0,0,255),3)
        
        numberPos.append(tempList)
    
        
    cv2.imshow("Image", img)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

    return numberPos, box, currentNumPos, bonusButtons, bingoButtton, rotation

def getCalibationData():
    with open('calibration.yaml') as f:
        data = yaml.load(f, Loader=yaml.Loader)
    numberPos, box, currentNumPos, bonusButtons, bingoButton, rotation  = data['numberPos'],data['box'],data['currentNumPos'],data['bonusButtons'],data['bingoButton'], data['rotation']
    
    return numberPos, box, currentNumPos, bonusButtons, bingoButton, rotation



if __name__ == '__main__':
    try:
        numberPos, box, currentNumPos, bonusButtons, bingoButton, rotation = calibrate()
        print("Calibration Succesfull")
        
        dictionary = {"numberPos": numberPos,
                      "box":box,
                      "currentNumPos": currentNumPos,
                      "bonusButtons":bonusButtons,
                      "bingoButton":bingoButton,
                      "rotation" : rotation
            }
        
        with open('calibration.yaml', 'w') as f:
            yaml.dump(dictionary, f)
            
            
    except Exception as e:
        print(e)
        print("Calibration Failed")
        cv2.destroyAllWindows()
        
    
    


