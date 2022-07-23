#include <Servo.h>
Servo servo1, servo2;
int tilt = 150;
void setup()
{
  servo1.attach(5);  //The Tilt servo is attached to pin 9.
  servo2.attach(6);
  Serial.begin(115200);  //Set up a serial connection for 57600 bps.
  Serial.println("Ready");
}


void loop() {
  static int v = 0;

  if (Serial.available()){
    
    char ch = Serial.read();
    Serial.println(ch);
    switch (ch) {
      case '0'...'9':
        v = v * 10 + ch - '0';
        break;

      case 'a':
        servo1.write(v);
        Serial.println(v);
        v = 0;
        break;
      case 'b':
        servo2.write(v);
        Serial.println(v);
        v = 0;
        break; }
  }
}
