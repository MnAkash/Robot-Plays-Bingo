# -*- coding: utf-8 -*-
'''
Serial Communication with arduino
----------------------------------
1. For board number selection will send --> x,y
    Where x and y are coordinate of the number to pressed considering top left as 0,0 and bottom right as 4,4

2. Solenoid up   --> 'u'

3. Solenoid down --> 'd'
'''

import serial, time
import serial.tools.list_ports

    
class robot:
    def __init__(self, baudrate=115200):
        self.home = [0,55]
        self.bingoCoords = [14,7]
        self.bonusCoords1 = [14,35]
        self.bonusCoords2 = [14,23]
        #Data points of four corner of number board with calibrated servo value
        self.servoPoints_X = [(0, 0, 85),(0, 4, 84),(4, 0, 30),(4, 4, 33)]
        self.servoPoints_Y = [(0, 0, 48),(0, 4, 5),(4, 0, 38),(4, 4, 0)]
        
        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if "CH340" in port.description:
                    self.arduino = serial.Serial(port=port.device,baudrate=baudrate)
                    try:
                        self.arduino.isOpen()
                    except:
                        self.arduino.close()
                        self.arduino.open()
                        
                    print("Connected to robot at port : ", port.device)
                    self.isOpen = True
                    
            self.goHome()
            
            
        except Exception as e:
            self.isOpen = False
            print(e)
            print("Could not connect to the Robot")
            #exit()
            
        
        
        
        
    def bilinear_interpolation(self, x, y, points):
        '''Interpolate (x,y) from values associated with four points.
    
        The four points are a list of four triplets:  (x, y, value).
        The four points can be in any order.  They should form a rectangle.
    
            >>> bilinear_interpolation(12, 5.5,
            ...                        [(10, 4, 100),
            ...                         (20, 4, 200),
            ...                         (10, 6, 150),
            ...                         (20, 6, 300)])
            165.0
    
        '''
        
        # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation
    
        points = sorted(points)               # order points by x, then by y
        (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points
    
        if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
            raise ValueError('points do not form a rectangle')
        if not x1 <= x <= x2 or not y1 <= y <= y2:
            raise ValueError('(x, y) not within the rectangle')
    
        return (q11 * (x2 - x) * (y2 - y) +
                q21 * (x - x1) * (y2 - y) +
                q12 * (x2 - x) * (y - y1) +
                q22 * (x - x1) * (y - y1)
               ) / ((x2 - x1) * (y2 - y1) + 0.0)

    
    def solenoidUP(self):
        if self.isOpen:
            self.arduino.write(bytes("u", 'utf-8'))
            
    def solenoidDOWN(self):
        if self.isOpen:
            self.arduino.write(bytes("d", 'utf-8'))
     
    def sendCoords(self, X, Y):
        #X, Y are global coordinates       
        dataToSend = str(int(X)) + "x" + str(int(Y)) + "y"
        if self.isOpen:
            self.arduino.write(bytes(dataToSend, 'utf-8'))
            
    def goHome(self):
        x = self.home[0]
        y= self.home[1]
        
        self.sendCoords(x, y)
        time.sleep(.5)
    
    def pressAndGoHome(self, X, Y):
        self.solenoidUP()
        time.sleep(0.05)
        self.sendCoords(X, Y)
        time.sleep(.5)#time to reach
        self.solenoidDOWN()
        time.sleep(0.2)#press for this long
        self.solenoidUP()#release
        time.sleep(0.05)
        self.goHome()#after release go home
        self.solenoidDOWN()
            
    def sendBoxCoords(self, box_X, box_Y):
        #Will receive coordinate for number box
        x = self.bilinear_interpolation(box_X, box_Y, self.servoPoints_X)
        y = self.bilinear_interpolation(box_X, box_Y, self.servoPoints_Y)
        
        self.pressAndGoHome(x, y)
        
        
    def pressBingo(self):
        x = self.bingoCoords[0]
        y= self.bingoCoords[1]
        
        print("Pressing Bingo")
        self.pressAndGoHome(x, y)
        
    def pressBonus1(self):
        x = self.bonusCoords1[0]
        y= self.bonusCoords1[1]
        
        print("Pressing Bonus1")
        self.pressAndGoHome(x, y)
    
    def pressBonus2(self):
        x = self.bonusCoords2[0]
        y= self.bonusCoords2[1]
        
        print("Pressing Bonus2")
        self.pressAndGoHome(x, y)
        
    def pressGimmeMore(self, position):
        '''
            1
        0       2
            3
        '''
        if position == 0:
            self.sendBoxCoords(2.5, 0.5)
        elif position == 1:
            self.sendBoxCoords(1,2)
        elif position == 2:
            self.sendBoxCoords(2.5,3.5)
        elif position == 3:
            self.sendBoxCoords(4,2)

    def testNumberBoard(self):
        for i in range(5):
            for j in range(5):
                r.sendBoxCoords(i, j)
                #time.sleep(.4)
                r.goHome()

    def testFullBoard(self):
        print("Pressing Top Left")
        r.sendBoxCoords(0, 0)
        print("Pressing Top Right")
        r.sendBoxCoords(0, 4)
        print("Pressing Bottom Left")
        r.sendBoxCoords(4, 0)
        print("Pressing Bottom Right")
        r.sendBoxCoords(4, 4)

        r.pressBonus1()
        r.pressBonus2()
        r.pressBingo()

        # print("Pressing Gimme More locations....")
        # r.pressGimmeMore(0)
        # r.pressGimmeMore(1)
        # r.pressGimmeMore(2)
        # r.pressGimmeMore(3)

        print("Test Complete!")

if __name__ == '__main__':
    r = robot()
    time.sleep(2)
    r.goHome()
    time.sleep(.5)

    r.testFullBoard()






#Inverse kinematics of the robot

# from math import sqrt, acos, atan, pi
# OFFSET1 = 25                      #motor1 offset along x_axis
# OFFSET2 = 85                      #motor2 offset along x_axis
# YAXIS = 180                        #motor heights above (0,0)
# LENGTH = 100


# x = 85
# y = 55


# if (x > OFFSET1):
#   d1 = sqrt((x - OFFSET1) * (x - OFFSET1) + (YAXIS - y) * (YAXIS - y))
#   angle1 = pi + acos(d1 / (2 * LENGTH)) - atan((x - OFFSET1) / (YAXIS - y))#radians
# else:
#   d1 = sqrt((OFFSET1 - x) * (OFFSET1 - x) + (YAXIS - y) * (YAXIS - y));
#   angle1 = pi + acos(d1 / (2 * LENGTH)) + atan((OFFSET1 - x) / (YAXIS - y))#radians


# if (x > OFFSET2):
#   d2 = sqrt((x- OFFSET2) * (x- OFFSET2) + (YAXIS - y) * (YAXIS - y))
#   angle2 = pi - acos(d2 / (2 * LENGTH)) - atan((x - OFFSET2) / (YAXIS - y))
# else:
#   d2 = sqrt((OFFSET2 - x) * (OFFSET2 - x) + (YAXIS - y) * (YAXIS - y))
#   angle2 = pi - acos(d2 / (2 * LENGTH)) + atan((OFFSET2 - x) / (YAXIS - y))


# angle1 = 180 - (angle1*180/pi -90)
# angle2 = 180 - (angle2*180/pi -90)
# #85x55y