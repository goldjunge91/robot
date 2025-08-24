/*
 *  Adapted for Arduino UNO + 2x TB6612 (4 motors), no encoders, ROS2 via serial.
 *  Derived from foxbot_core (GPLv3) – this file remains GPLv3.
 */

#ifndef FOXBOT_CORE_CONFIG_H_
#define FOXBOT_CORE_CONFIG_H_

// ===== Plattform: Arduino UNO =====
// PWM ist 8-bit (0..255)
#define PWM_MAX          255
#define WATCHDOG_MS      300
#define LOOP_MS          10    // Regeltakt für Rampen
#define DEADZONE_DEFAULT 25    // PWM-Offset, damit die Räder anlaufen
#define SLEW_DEFAULT     6     // max. PWM-Schritt pro LOOP_MS

// ===== Pinbelegung TB6612 x2 =====
// Links (Board L): zwei Motoren
//   Motor L1
#define L1_PWM   5   // PWM
#define L1_IN1   4
#define L1_IN2   7
//   Motor L2
#define L2_PWM   6   // PWM
#define L2_IN1   8
#define L2_IN2   12

// Rechts (Board R): zwei Motoren
//   Motor R1
#define R1_PWM   9   // PWM
#define R1_IN1   10
#define R1_IN2   13
//   Motor R2
#define R2_PWM   11  // PWM
#define R2_IN1   A0  // als Digitalpin
#define R2_IN2   A1  // als Digitalpin

// Optional: STBY per Pin (sonst einfach dauernd auf 5V legen)
#define USE_STBY_PIN    0
#define STBY_PIN        A2

// ===== Trim/Kalibrierung (zum Ausgleichen mechanischer Unterschiede) =====
#define TRIM_L1   0
#define TRIM_L2   0
#define TRIM_R1   0
#define TRIM_R2   0

#endif // FOXBOT_CORE_CONFIG_H_
