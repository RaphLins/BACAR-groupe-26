#include <bacarMotor.h>

BacarMotor droit(9, 7, 8);
BacarMotor gauche(10, 11, 12);
float VG = 0.54; //Vitesse max moteur gauche
float VD = 0.53; //Vitesse max moteur droit
bool ledState;

void setup(){
  gauche.begin();
  droit.begin();
  gauche.actuate(tGauche);
  droit.actuate(tDroit);
}

void loop(){
}
