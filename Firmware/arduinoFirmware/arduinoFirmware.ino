#include <Servo.h>

Servo leftServo, rightServo;

const int leftServoPin = 5;
const int rightServoPin = 6;
const int solenoid = 11;
void setup() {
  pinMode(solenoid, OUTPUT);
  
  leftServo.attach(leftServoPin);
  rightServo.attach(rightServoPin);

  leftServo.write(90);
  rightServo.write(90);
}

void loop() {
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
  delay(1000);
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
