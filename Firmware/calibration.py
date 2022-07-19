# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pandas as pd
import time
import yaml

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
            cv2.destroyAllWindows()
            break
        
    while True:
    
        _, img = capture.read()
    
        imgContour = img.copy()
        
        imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(7,7),1)
        imgCanny = cv2.Canny(imgBlur,50,50)
        
        
        squares, circles = getContours(imgCanny, imgContour)
        
        allSquares += squares       
    
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #time.sleep(5)
            break
    
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
    
    #3.85, -1.85 is the location of relative loaction of random number appearing from initial position
    currentNumPos =  unitVector*np.array([3.8, -1.65]) + initialPos
    #append end point to currentNumPos array
    currentNumPos = np.append(currentNumPos, currentNumPos+np.array([box, box*1.15]))
    #Convert everything to int
    currentNumPos = currentNumPos.astype(int).tolist()
    
    
    #=====================================Calculating two bonus buttons location
    
    #0.45, 5.8 is the location of relative loaction of 1st bonus button from initial position
    bonusButton1 =  unitVector*np.array([0.45, 5.5]) + initialPos
    #append end point of 1st bonus button to bonusButton1 array
    bonusButton1 = np.append(bonusButton1, bonusButton1+np.array([box*0.7, box*0.7]))
    
    #1.5, 5.8 is the location of relative loaction of 2nd bonus button from initial position
    bonusButton2 =  unitVector*np.array([1.5, 5.5]) + initialPos
    #append end point of 2nd bonus button to bonusButton1 array
    bonusButton2 = np.append(bonusButton2, bonusButton2+np.array([box*0.7, box*0.7]))
    
    #Append both both button location in one 2d array
    bonusButtons = np.append(bonusButton1, bonusButton2).reshape(2,4)
    
    #Convert everything to int
    bonusButtons = bonusButtons.astype(int).tolist()
    
    
    
    #=====================================Calculating bingo button location
    
    #2.9, 5.6 is the location of relative loaction of bingo button from initial position
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
    cv2.waitKey(1500)
    cv2.destroyAllWindows()

    return numberPos, box, currentNumPos, bonusButtons, bingoButtton

def getCalibationData():
    with open('calibration.yaml') as f:
        data = yaml.load(f, Loader=yaml.Loader)
    numberPos, box, currentNumPos, bonusButtons, bingoButton  = data['numberPos'],data['box'],data['currentNumPos'],data['bonusButtons'],data['bingoButton']
    
    return numberPos, box, currentNumPos, bonusButtons, bingoButton



if __name__ == '__main__':
    numberPos, box, currentNumPos, bonusButtons, bingoButton = calibrate()
    
    dictionary = { "numberPos": numberPos,
                  "box":box,
                  "currentNumPos": currentNumPos,
                  "bonusButtons":bonusButtons,
                  "bingoButton":bingoButton
        }
    
    with open('calibration.yaml', 'w') as f:
        yaml.dump(dictionary, f)
    
    