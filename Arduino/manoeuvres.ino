#include <bacarMotor.h>
#include <bacarComm.h>

BacarComm comm;
BacarMotor droit(9, 7, 8);
BacarMotor gauche(10, 11, 12);
float VG = 0.54;
float VD = 0.53;
int pinSensorG = 15;
int pinSensorM = 16;
int pinSensorD = 17;
int sensorG;
int sensorM;
int sensorD;
int currentMan = 0;

void setup(){
  comm.begin();
  pinMode(pinSensorG, INPUT);
  pinMode(pinSensorM, INPUT);
  pinMode(pinSensorD, INPUT);
  gauche.begin();
  droit.begin();
}

void loop(){
  int32_t x, y;
  float u, v;
  // Vérifie si un nouveau message de l'Orange PI a été reçu
  if (comm.newMessage() == true) {
    // On lit les 4 valeurs contenues dans le message
    x = comm.xRead();
    y = comm.yRead();
    u = comm.uRead();
    v = comm.vRead();
    // et on les renvoie à l'Orange PI
    comm.sendMessage(x, y, u, v);
    if (x != 0) currentMan = x;

    if(currentMan != 0){
      if (currentMan==11) {man_1_1(); currentMan=0;}
      else if (currentMan==12) {man_1_2(); currentMan=0;}
      else if (currentMan==13) {man_1_3(); currentMan=0;}
      else if (currentMan==14) {man_1_4();}
      else if (currentMan==15) {man_1_5();}
      else if (currentMan==16) {man_1_6();}
      else if (currentMan==21) {man_2_1(); currentMan=0;}
      else if (currentMan==22) {man_2_2(); currentMan=0;}
      else if (currentMan==23) {man_2_3(); currentMan=0;}
      else if (currentMan==24) {man_2_4(); currentMan=0;}
      else if (currentMan==25) {man_2_5(); currentMan=0;}
    }
    
  }
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
  avancer(VG*1.2, VD*0.91, 11600);
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
  avancer(1700);
  delay(500);
  avancer(-VG, 0, 500);
  avancer(-VG*1.2, -VD*1.2, 600);
  avancer(0, -VD, 500);
}
void man_2_5(){//demi-tour
  avancer(1500);
  delay(500);
  avancer(-VG, 0, 1000);
  avancer(0, VD, 750);
  avancer(900);
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
  droit.actuate(VD*0.6);
  gauche.actuate(-VG*0.6);
  delay(750);
  gauche.halt();
  droit.halt();
}


