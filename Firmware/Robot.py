# -*- coding: utf-8 -*-
import serial, time
import serial.tools.list_ports

        
class robot:
    def __init__(self, port='COM5',baudrate=115200):
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
        except Exception as e:
            self.isOpen = False
            print(e)
            print("Could not connect to the Robot")
            #exit()
            
        
        self.home = [65,55]
        #Data points of four corner of number board with calibrated servo value
        self.leftServoPoints = [(0, 0, 108),(0, 4, 87),(4, 0, 81),(4, 4, 61)]
        self.rightServoPoints = [(0, 0, 102),(0, 4, 117),(4, 0, 76),(4, 4, 98)]
        self.bingoCoords = [56,89]
        self.bonusCoords1 = [72,70]
        self.bonusCoords2 = [67,77]
        
        
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

    def sendCoords(self, X, Y):
        left = self.bilinear_interpolation(X, Y, self.leftServoPoints)
        right = self.bilinear_interpolation(X, Y, self.rightServoPoints)
        
        dataToSend = str(int(left)) + "l" + str(int(right)) + "r"
        if self.isOpen:self.arduino.write(bytes(dataToSend, 'utf-8'))
        
    def sendServoPos(self, left, right):
        dataToSend = str(int(left)) + "l" + str(int(right)) + "r"
        if self.isOpen:self.arduino.write(bytes(dataToSend, 'utf-8'))
    
    def pressBingo(self):
        left = self.bingoCoords[0]
        right= self.bingoCoords[1]
        
        self.sendServoPos(left, right)
        
    def pressBonus1(self):
        left = self.bonusCoords1[0]
        right= self.bonusCoords1[1]
        
        self.sendServoPos(left, right)
    
    def pressBonus2(self):
        left = self.bonusCoords2[0]
        right= self.bonusCoords2[1]
        
        self.sendServoPos(left, right)
        
    def pressHome(self):
        left = self.home[0]
        right= self.home[1]
        
        dataToSend = str(int(left)) + "l" + str(int(right)) + "r"
        if self.isOpen:self.arduino.write(bytes(dataToSend, 'utf-8'))



