/******************************************************************************
TestRun.ino
TB6612FNG H-Bridge Motor Driver Example code
Michelle @ SparkFun Electronics
8/20/16
https://github.com/sparkfun/SparkFun_TB6612FNG_Arduino_Library

Uses 2 motors to show examples of the functions in the library.  This causes
a robot to do a little 'jig'.  Each movement has an equal and opposite movement
so assuming your motors are balanced the bot should end up at the same place it
started.

Resources:
TB6612 SparkFun Library

Development environment specifics:
Developed on Arduino 1.6.4
Developed with ROB-9457
******************************************************************************/

// This is the library for the TB6612 that contains the class Motor and all the
// functions
#include <SparkFun_TB6612.h>
#include <SparkFun_TB6612.h>

// Pins (ein TB6612, 2 Motoren)
#define AIN1 2
#define AIN2 4
#define PWMA 5   // PWM
#define BIN1 7
#define BIN2 8
#define PWMB 6   // PWM
#define STBY 9

// Richtungskorrektur (1 oder -1)
const int offsetA = 1;
const int offsetB = 1;

Motor motorA(AIN1, AIN2, PWMA, offsetA, STBY);
Motor motorB(BIN1, BIN2, PWMB, offsetB, STBY);

void setup() { /* Library setzt pinMode selbst */ }

void loop() {
  // Einzelmotor vor/zurück
  motorA.drive(200, 1000); motorA.brake(); delay(400);
  motorB.drive(200, 1000); motorB.brake(); delay(400);

  // Beide vor/zurück/links/rechts
  forward(motorA, motorB, 150); delay(1000); brake(motorA, motorB); delay(400);
  back(motorA, motorB, 150);    delay(1000); brake(motorA, motorB); delay(400);
  left(motorA, motorB, 120);    delay(800);
  right(motorA, motorB, 120);   delay(800);
  brake(motorA, motorB);        delay(600);
}
