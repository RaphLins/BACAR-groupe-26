#include <bacarMotor.h>
BacarMotor droit(9, 7, 8);
BacarMotor gauche(10, 11, 12);
int VG = 0.5;
int VD = 0.49;
int pinSensorG = 15;
int pinSensorM = 16;
int pinSensorD = 17;
int sensorG;
int sensorM;
int sensorD;

void setup(){
  pinMode(pinSensorG, INPUT);
  pinMode(pinSensorM, INPUT);
  pinMode(pinSensorD, INPUT);
  gauche.begin();
  droit.begin();
}

void loop(){
}

void man_1_1(){//5s
  avancer(5000);
}
void man_1_2(){//1m
  avancer(4000);
}
void man_1_3(){
  avancer(3000);
  delay(2000);
  avancer(2000);
}
void man_1_4(){//stop si detecteur frontal
  sensorM = digitalRead(pinSensorM);
  if (sensorM == HIGH) arret();
  else avancer();
}
void man_1_5(){//stop si capteurs de bord
  sensorG = digitalRead(pinSensorG);
  sensorD = digitalRead(pinSensorD);
  if (sensorG == HIGH or sensorD == HIGH) arret();
  else avancer();
}
void man_1_6(){//suit la chaussee avec capteurs de bord
  sensorG = digitalRead (pinSensorG);
  sensorD = digitalRead (pinSensorD);
  if (sensorG == HIGH) avancer(VG, 0);
  else if (sensorD == HIGH) avancer(0,VD);
  else if (sensorD == HIGH && sensorG == HIGH) arret();
  else avancer();
}
void man_2_1(){//1m droit
  avancer(4000);
}
void man_2_2(){//Cercle
  avancer(VG*1.2, VD*0.9, 11500);
}
void man_2_3(){//Carre
  avancer(1200);
  tourner(90);
  avancer(1200);
  tourner(90);
  avancer(1200);
  tourner(90);
  avancer(1200);
}
void man_2_4(){//Creneau
  avancer(1500);
  delay(500);
  avancer(-VG, 0, 500);
  avancer(-VG*1.2, -VD*1.2, 900);
  avancer(0, -VD, 500);
}
void man_2_5(){//demi-tour
  avancer(1000);
  delay(500);
  avancer(-VG, 0, 1000);
  avancer(0, VD, 750);
  avancer(500);
}

void avancer(int duree){
  gauche.actuate(VG);
  droit.actuate(VD);
  delay(duree);
  gauche.halt();
  droit.halt();
}
void avancer(float tGauche,float tDroit){
  gauche.actuate(tGauche);
  droit.actuate(tDroit);
}
void avancer(float tGauche,float tDroit, int duree){
  gauche.actuate(tGauche);
  droit.actuate(tDroit);
  delay(duree);
  gauche.halt();
  droit.halt();
}
void avancer(){
  droit.actuate(VD);
  gauche.actuate(VG);
}
void arret(){
  gauche.halt();
  droit.halt();
}
void tourner(int angle){
  droit.actuate(0.3);
  gauche.actuate(-0.3);
  delay(1000*angle/90);
  gauche.halt();
  droit.halt();
}


