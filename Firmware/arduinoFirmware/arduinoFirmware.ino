#include <Servo.h>
Servo leftServo, rightServo;

const int leftServoPin = 5;
const int rightServoPin = 6;
const int solenoid = 11;
int X, Y;//To store coordinate from serial command


//1 denotes left, 2 denotes right
const int x1=102, y1=108;//Top left
const int x2=117, y2=87;//Top right
const int x3=97, y3=66;//Bottom right
const int x4=76, y4=81;//Bottom left

void setup() {
  pinMode(solenoid, OUTPUT);
  
  leftServo.attach(leftServoPin);
  rightServo.attach(rightServoPin);

  leftServo.write(90);
  rightServo.write(90);
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
        X = ch.toInt();
        Serial.read();//Read next ,(comma)
        ch = Serial.read();
        Y = ch.toInt();
        coord2servo(X, Y);
        
        break;

      case 'B':
        pressBingo();
        break;
        
      case 'M':
        pressBonus1();
        
        break;
      case 'N':
        pressBonus2();
        
        break;
    }
  }
}


void coord2servo(int x, int y){
  
}

void pressBingo(){
  
}
void pressBonus1(){
  
}
void pressBonus2(){
  
}


void solenoidUp(){
  digitalWrite(solenoid, HIGH);
}
void solenoidDown(){
  digitalWrite(solenoid, LOW);
}

void servo(int left, int right){
  leftServo.write(left);
  rightServo.write(right);
}
