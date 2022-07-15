# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pandas as pd
import time

class point:
    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.number = ''


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
            print(len(approx))
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)

            if objCor ==3: objectType ="Tri"
            elif objCor == 4:
                aspRatio = w/float(h)
                if aspRatio >0.9 and aspRatio <1.1: objectType= "Square"
                else:objectType="Rectangle"
            elif objCor>4: objectType= "Circle"
            else:objectType="None"

            
            if objectType == "Square" or objectType =="Circle":
                if objectType == "Square":squares.append( (x,y,w,h) )
                else: circles.append( (x,y,w,h) )

                cv2.rectangle(imgContour,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.putText(imgContour,objectType,
                            (x+(w//2)-10,y+(h//2)-10),cv2.FONT_HERSHEY_COMPLEX,0.7,
                            (0,0,0),2)
    
    cv2.imshow("Image", imgContour)
    return squares, circles



def calibrate():
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    allSquares = []
    allCircles = []
    
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
        allCircles += circles
        
        
        
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #time.sleep(5)
            break
    
    capture.release()
    cv2.destroyAllWindows()
    
    
    #allCircles = list(set(allCircles))
    allCirclesDF = pd.DataFrame.from_records(allCircles, columns =['X', 'Y', 'W', 'H'])
    
    
    allSquares = list(set(allSquares))
    allSquaresDF = pd.DataFrame.from_records(allSquares, columns =['X', 'Y', 'W', 'H'])
    xmin, ymin, wmin, hmin = allSquaresDF.min()
    xmax, ymax, wmax, hmax = allSquaresDF.max()
    
    box = int((xmax - xmin)/4)
    
    #Getting y min value for this corner circle, since it is at the top
    numberDisplayPositions = allCirclesDF[allCirclesDF['Y'] == allCirclesDF.min()[1]].iloc[0]
    numberDisplayPos = (numberDisplayPositions[0], numberDisplayPositions[1])
    
    allPoints = []
    for i in range(5):
        tempList = []
        for j in range(5):
            tempList.append(point(xmin+j*box, ymin+i*box))
            cv2.circle(img,(xmin+i*box,ymin+j*box),5,(0,0,255),3)
        
        allPoints.append(tempList)
    
    cv2.circle(img,numberDisplayPos,8,(0,0,255),3)
    
    
    cv2.imshow("Image", img)
    
    return allPoints, numberDisplayPos, box


