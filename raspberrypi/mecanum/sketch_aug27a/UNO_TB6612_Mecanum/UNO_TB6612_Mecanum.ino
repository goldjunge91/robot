/*
 * UNO + 2x TB6612 (SparkFun_TB6612) – Serial Control for 4 Mecanum Wheels
 * v2.6 - Updated with modern Arduino String parsing and a new COAST command.
 *
 * Serial Commands (terminate with '\n'):
 * M <X%> <Y%> <Z%> : Move with X (strafe), Y (forward), and Z (rotation) components.
 * D <FL%> <FR%> <RL%> <RR%> : Drive each wheel directly with a percentage value.
 * T <MOTOR> <SPEED%> : Test a single motor (MOTOR = FL, FR, RL, RR).
 * STOP               : Immediately BRAKE all motors (active stop).
 * COAST              : Immediately let all motors COAST (spin down freely).
 * PING               : Responds with "PONG".
 * VER?               : Responds with the firmware version string.
 * DUMP               : Prints the current PWM value for each motor.
 */

#include <SparkFun_TB6612.h>
#include <math.h>
#include "robot_core_config.h"

// ---------- All hardware pins and tuning values are in robot_core_config.h ----------

// Motor objects for 4 mecanum wheels
Motor motorFL(FL_IN1, FL_IN2, FL_PWM, OFFSET_FL, STBY_L);
Motor motorRL(RL_IN1, RL_IN2, RL_PWM, OFFSET_RL, STBY_L);
Motor motorFR(FR_IN1, FR_IN2, FR_PWM, OFFSET_FR, STBY_R);
Motor motorRR(RR_IN1, RR_IN2, RR_PWM, OFFSET_RR, STBY_R);

// Variables to store the current PWM values for debugging
int currentPwmFL = 0, currentPwmFR = 0, currentPwmRL = 0, currentPwmRR = 0;

// Flag to ensure the watchdog message is only printed once
bool watchdogTriggered = false;

// Watchdog timer variable
unsigned long lastCmdMs = 0;


// --- Utility Functions ---

// Constrains a value to the -PWM_MAX to PWM_MAX range
static inline int clampPwm(int x) {
  return constrain(x, -PWM_MAX, PWM_MAX);
}

// Converts a percentage [-100..100] to a PWM value [-PWM_MAX..PWM_MAX]
int pctToPwm(int pct) {
  long val = (long)constrain(pct, -100, 100) * PWM_MAX / 100;
  return (int)val;
}

// --- Motor Control Functions ---

// Resets all motor PWM values to 0 for tracking
void resetPwmValues() {
  currentPwmFL = 0;
  currentPwmFR = 0;
  currentPwmRL = 0;
  currentPwmRR = 0;
}

// Brakes all four motors (active stop)
void hardStop() {
  motorFL.brake();
  motorFR.brake();
  motorRL.brake();
  motorRR.brake();
  resetPwmValues();
  Serial.println(F("DEBUG: Motors BRAKED."));
}

// Lets all four motors coast (spin freely to a stop)
void coastAll() {
  motorFL.drive(0);
  motorFR.drive(0);
  motorRL.drive(0);
  motorRR.drive(0);
  resetPwmValues();
  Serial.println(F("DEBUG: Motors COASTING."));
}


void setup() {
  Serial.begin(115200);
  // Wait for serial to stabilize. A longer delay can help prevent issues after upload.
  delay(1500);
  lastCmdMs = millis();
  Serial.println(F("BOOT UNO_TB6612_MECANUM v2.6"));
}

// --- Main Command Parser ---
void parseLine(String line) {
  line.trim(); // Remove leading/trailing whitespace
  if (line.length() == 0) return;

  // A command was received, so reset the watchdog timer and flag
  lastCmdMs = millis();
  watchdogTriggered = false;

  // --- Move Command (Holonomic) ---
  if (line.startsWith("M ")) {
    int xPct, yPct, zPct;
    if (sscanf(line.c_str() + 2, "%d %d %d", &xPct, &yPct, &zPct) == 3) {
      float raw_FL = yPct + xPct + zPct;
      float raw_FR = yPct - xPct - zPct;
      float raw_RL = yPct - xPct + zPct;
      float raw_RR = yPct + xPct - zPct;

      float max_raw = fmax(fabs(raw_FL), fmax(fabs(raw_FR), fmax(fabs(raw_RL), fabs(raw_RR))));
      float scale = (max_raw > 100.0) ? 100.0 / max_raw : 1.0;

      currentPwmFL = clampPwm(pctToPwm(raw_FL * scale) + TRIM_FL);
      currentPwmFR = clampPwm(pctToPwm(raw_FR * scale) + TRIM_FR);
      currentPwmRL = clampPwm(pctToPwm(raw_RL * scale) + TRIM_RL);
      currentPwmRR = clampPwm(pctToPwm(raw_RR * scale) + TRIM_RR);
      
      motorFL.drive(currentPwmFL);
      motorFR.drive(currentPwmFR);
      motorRL.drive(currentPwmRL);
      motorRR.drive(currentPwmRR);

      Serial.print(F("ACK M ")); Serial.print(xPct); Serial.print(' ');
      Serial.print(yPct); Serial.print(' '); Serial.println(zPct);
    } else {
      Serial.println(F("ERR M SYNTAX"));
    }
    return;
  }

  // --- Direct Drive Command (Individual Wheels) ---
  if (line.startsWith("D ")) {
    int fl_pct, fr_pct, rl_pct, rr_pct;
    if (sscanf(line.c_str() + 2, "%d %d %d %d", &fl_pct, &fr_pct, &rl_pct, &rr_pct) == 4) {
      currentPwmFL = clampPwm(pctToPwm(fl_pct) + TRIM_FL);
      currentPwmFR = clampPwm(pctToPwm(fr_pct) + TRIM_FR);
      currentPwmRL = clampPwm(pctToPwm(rl_pct) + TRIM_RL);
      currentPwmRR = clampPwm(pctToPwm(rr_pct) + TRIM_RR);
      
      motorFL.drive(currentPwmFL);
      motorFR.drive(currentPwmFR);
      motorRL.drive(currentPwmRL);
      motorRR.drive(currentPwmRR);

      Serial.print(F("ACK D ")); Serial.print(fl_pct); Serial.print(' ');
      Serial.print(fr_pct); Serial.print(' '); Serial.print(rl_pct); Serial.print(' '); Serial.println(rr_pct);
    } else {
      Serial.println(F("ERR D SYNTAX"));
    }
    return;
  }
  
  // --- Motor Test Command ---
  if (line.startsWith("T ")) {
    char motorStr[3] = {0};
    int pct;
    if (sscanf(line.c_str() + 2, "%2s %d", motorStr, &pct) == 2) {
      hardStop(); // Stop all motors for a clean test
      int pwm = pctToPwm(pct);
      
      if (strcmp(motorStr, "FL") == 0) motorFL.drive(currentPwmFL = clampPwm(pwm + TRIM_FL));
      else if (strcmp(motorStr, "FR") == 0) motorFR.drive(currentPwmFR = clampPwm(pwm + TRIM_FR));
      else if (strcmp(motorStr, "RL") == 0) motorRL.drive(currentPwmRL = clampPwm(pwm + TRIM_RL));
      else if (strcmp(motorStr, "RR") == 0) motorRR.drive(currentPwmRR = clampPwm(pwm + TRIM_RR));
      else { Serial.println(F("ERR T MOTOR")); return; }

      Serial.print(F("ACK T ")); Serial.print(motorStr); Serial.print(" "); Serial.println(pct);
    } else {
      Serial.println(F("ERR T SYNTAX"));
    }
    return;
  }

  // --- Stop and Coast Commands ---
  if (line.equals("STOP")) {
    hardStop();
    Serial.println(F("ACK STOP"));
    return;
  }

  if (line.equals("COAST")) { // --- NEW COMMAND ---
    coastAll();
    Serial.println(F("ACK COAST"));
    return;
  }
  
  // --- Utility Commands ---
  if (line.equals("DUMP")) {
    Serial.print(F("DUMP: FL=")); Serial.print(currentPwmFL);
    Serial.print(F(" FR=")); Serial.print(currentPwmFR);
    Serial.print(F(" RL=")); Serial.print(currentPwmRL);
    Serial.print(F(" RR=")); Serial.println(currentPwmRR);
    return;
  }

  if (line.equals("PING")) { Serial.println(F("PONG")); return; }
  if (line.equals("VER?")) { Serial.println(F("UNO_TB6612_MECANUM v2.6")); return; }

  // --- Unknown Command ---
  Serial.println(F("ERR CMD UNKNOWN"));
}


void loop() {
  // --- REFACTORED: Simplified Serial Handling ---
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    parseLine(line);
  }

  // Watchdog timer to stop the robot if commands cease.
  if (millis() - lastCmdMs > WATCHDOG_MS) {
    if (!watchdogTriggered) {
      hardStop(); // Default safety action is to brake
      Serial.println(F("DEBUG: Watchdog triggered. Hard stop engaged."));
      watchdogTriggered = true;
    }
  }
}