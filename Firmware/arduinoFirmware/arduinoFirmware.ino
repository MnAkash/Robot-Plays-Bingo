#include <Servo.h>
Servo servo1, servo2;


// ----- constants
#define PI 3.141592653589793


const int pinServo2 = 5;
const int pinServo1 = 6;
const int solenoid = 11;
int coordX, coordY;//To store coordinate from serial command
static int v = 0;

//Inverser Kinematics variables
float            //stylus distance to motor2
angle1,               //motor1 angle
angle2;               //motor2 angle

float
OFFSET1 = 25,                      //motor1 offset along x_axis
OFFSET2 = 85,                      //motor2 offset along x_axis
YAXIS = 180,                        //motor heights above (0,0)
LENGTH = 100;                       //length of each arm-segment


void setup() {
  Serial.begin(115200);
  pinMode(solenoid, OUTPUT);
  
  servo2.attach(pinServo2);
  servo1.attach(pinServo1);

  servo2.write(90);
  servo1.write(90);
}

void loop() {
  /*
  solenoidUp();
  delay(500);
  servo(90, 90);
  delay(1000);
  solenoidDown();
  delay(200);
  solenoidUp();
  delay(500);
  servo(50, 50);
  delay(1000);
  solenoidDown();
  delay(1000);*/

  if (Serial.available()){
    
    char ch = Serial.read();
    Serial.print(ch);
    switch (ch) {
      case '0'...'9':
        v = v * 10 + ch - '0';
        break;

      case 'x':
        coordX = v;
        v = 0;
        break;
      case 'y':
        coordY = v;
        
        moveTo(coordX, coordY);
        v = 0;
        break;

    }
  }
}


void moveTo(int x, int y){
  inverse_kinematics(x, y);
//  solenoidUp();
//  delay(50);
  servo(angle1, angle2);
//  delay(200);
//  solenoidDown();
//  delay(200);
//  solenoidUp();
//  delay(200);
}


void inverse_kinematics(float x, float y) {
  float
  d1,            //stylus distance to motor1
  d2;             //stylus distance to motor1

  
  // ----- calculate motor1 angle when pen at (x,y)
  if (x > OFFSET1) {
    d1 = sqrt((x - OFFSET1) * (x - OFFSET1) + (YAXIS - y) * (YAXIS - y));
    angle1 = PI + acos(d1 / (2 * LENGTH)) - atan((x - OFFSET1) / (YAXIS - y)); //radians
  } else {
    d1 = sqrt((OFFSET1 - x) * (OFFSET1 - x) + (YAXIS - y) * (YAXIS - y));
    angle1 = PI + acos(d1 / (2 * LENGTH)) + atan((OFFSET1 - x) / (YAXIS - y)); //radians
  }

  // ----- calculate motor2 angle when pen at start position (0,0)
  if (x > OFFSET2) {
    d2 = sqrt((x- OFFSET2) * (x- OFFSET2) + (YAXIS - y) * (YAXIS - y));
    angle2 = PI - acos(d2 / (2 * LENGTH)) - atan((x - OFFSET2) / (YAXIS - y)); //radians
  } else {
    d2 = sqrt((OFFSET2 - x) * (OFFSET2 - x) + (YAXIS - y) * (YAXIS - y));
    angle2 = PI - acos(d2 / (2 * LENGTH)) + atan((OFFSET2 - x) / (YAXIS - y)); //radians
  }

  angle1 = (int)(180 - (angle1*180/PI - 90) );
  angle2 = (int)(180 - (angle2*180/PI - 90) );


  Serial.print(angle1);
  Serial.print(",");
  Serial.println(angle2);
}



void solenoidUp(){
  digitalWrite(solenoid, HIGH);
}
void solenoidDown(){
  digitalWrite(solenoid, LOW);
}

void servo(int angle1_value, int angle2_value){
  servo1.write(angle1_value);
  servo2.write(angle2_value);
}
