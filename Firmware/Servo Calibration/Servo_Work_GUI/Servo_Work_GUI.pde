//Processing code:
import processing.serial.*;       
import controlP5.*;

ControlP5 cp5;

int tilt = 90, pan = 90;

Serial myPort;

void setup()  {
  size(500, 250);
  myPort = new Serial(this, "COM5", 115200);
  cp5 = new ControlP5(this);

cp5.addSlider("pan")
.setPosition(50,70)
.setSize(300,30)
.setRange(0,180)
.setValue(90)
;

cp5.addSlider("tilt")
.setPosition(50,130)
.setSize(300,30)
.setRange(0,180)
.setValue(90)
;
}

void draw()  {
  println(tilt);
  myPort.write(tilt+"a");
  myPort.write(pan+"b");
}
