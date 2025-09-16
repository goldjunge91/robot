// Mecanum drive control for four TT motors with TB6612FNG
// Replace diffdrive_arduino with this sketch

#include <Arduino.h>

// Motor pin definitions (placeholder values)
// Front Left Motor
const int FL_PWM = 5;   // PWM pin
const int FL_IN1 = 2;   // Direction pin 1
const int FL_IN2 = 3;   // Direction pin 2

// Front Right Motor
const int FR_PWM = 6;
const int FR_IN1 = 4;
const int FR_IN2 = 7;

// Rear Left Motor
const int RL_PWM = 9;
const int RL_IN1 = 8;
const int RL_IN2 = 11;

// Rear Right Motor
const int RR_PWM = 10;
const int RR_IN1 = 12;
const int RR_IN2 = 13;

// Robot geometry (meters)
const float L = 0.1; // half length
const float W = 0.1; // half width
const float R = 0.04; // wheel radius

// Maximum PWM value
const int PWM_MAX = 255;

void setupMotor(int pwmPin, int in1Pin, int in2Pin) {
  pinMode(pwmPin, OUTPUT);
  pinMode(in1Pin, OUTPUT);
  pinMode(in2Pin, OUTPUT);
  analogWrite(pwmPin, 0);
  digitalWrite(in1Pin, LOW);
  digitalWrite(in2Pin, LOW);
}

void setMotor(int pwmPin, int in1Pin, int in2Pin, int speed) {
  speed = constrain(speed, -PWM_MAX, PWM_MAX);
  if (speed >= 0) {
    digitalWrite(in1Pin, HIGH);
    digitalWrite(in2Pin, LOW);
    analogWrite(pwmPin, speed);
  } else {
    digitalWrite(in1Pin, LOW);
    digitalWrite(in2Pin, HIGH);
    analogWrite(pwmPin, -speed);
  }
}

void setup() {
  Serial.begin(115200);
  setupMotor(FL_PWM, FL_IN1, FL_IN2);
  setupMotor(FR_PWM, FR_IN1, FR_IN2);
  setupMotor(RL_PWM, RL_IN1, RL_IN2);
  setupMotor(RR_PWM, RR_IN1, RR_IN2);
}

void loop() {
  if (Serial.available()) {
    float vx = Serial.parseFloat();
    float vy = Serial.parseFloat();
    float omega = Serial.parseFloat();

    if (Serial.read() == '\n') {
      // Mecanum kinematics
      float fl = (1.0 / R) * (vx - vy - (L + W) * omega);
      float fr = (1.0 / R) * (vx + vy + (L + W) * omega);
      float rl = (1.0 / R) * (vx + vy - (L + W) * omega);
      float rr = (1.0 / R) * (vx - vy + (L + W) * omega);

      int fl_pwm = (int)(fl * PWM_MAX);
      int fr_pwm = (int)(fr * PWM_MAX);
      int rl_pwm = (int)(rl * PWM_MAX);
      int rr_pwm = (int)(rr * PWM_MAX);

      setMotor(FL_PWM, FL_IN1, FL_IN2, fl_pwm);
      setMotor(FR_PWM, FR_IN1, FR_IN2, fr_pwm);
      setMotor(RL_PWM, RL_IN1, RL_IN2, rl_pwm);
      setMotor(RR_PWM, RR_IN1, RR_IN2, rr_pwm);
    }
  }
}
