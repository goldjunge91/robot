/*
 *  ROBOT_core – UNO open-loop (no encoders), 2x TB6612, 4 motors
 *  GPLv3 – derived work
 */

#ifndef ROBOT_CORE_CONFIG_H_
#define ROBOT_CORE_CONFIG_H_

// ===== Laufzeit-Defaults =====
#define PWM_MAX            255   // UNO PWM 8-bit
#define WATCHDOG_MS        300   // Stop, wenn solange kein Kommando
#define LOOP_MS            10    // Regeltakt (ms)
#define DEADZONE_DEFAULT   30    // 0..80 (Anlauf-Offset)
#define SLEW_DEFAULT       8     // 1..30 (max. PWM-Änderung pro LOOP_MS)

// ===== Offset Motoren(UNO) =====
// Richtungskorrektur: 1 oder -1 (wenn "vorwärts" falsch herum ist)
const int offsetMotor1 = 1;
const int offsetMotor2 = 1;
const int offsetMotor3 = 1;
const int offsetMotor4 = 1;


// ===== Verkabelung TB6612 (UNO) =====
// Linkes Board (2 Motoren)
#define L_AIN1   2
#define L_AIN2   4 // Motor 1
#define L_BIN1   7
#define L_BIN2   8 // Motor 2
#define L_PWMA   5
#define L_PWMB   6
#define L_STBY   A2   // kann unbenutzt bleiben, wenn STBY physisch an 5V

// Rechtes Board (2 Motoren)
#define R_AIN1   0
#define R_AIN2   1
#define R_BIN1   11
#define R_BIN2   12
#define R_PWMA   9
#define R_PWMB   10
#define R_STBY   A3   // kann unbenutzt bleiben, wenn STBY physisch an 5V

// ===== Motor-Offsets (1 oder -1) – Software-"Umpolen"
#define OFFSET_L1   1
#define OFFSET_L2   1
#define OFFSET_R1   1
#define OFFSET_R2   1

// Feintrimm je Motor (PWM-Offset in Schritten, zum Geradeauslauf)
#define TRIM_L1     0
#define TRIM_L2     0
#define TRIM_R1     0
#define TRIM_R2     0

#endif // ROBOT_CORE_CONFIG_H_
