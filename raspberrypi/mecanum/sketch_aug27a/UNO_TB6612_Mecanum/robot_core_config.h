#ifndef ROBOT_CORE_CONFIG_H
#define ROBOT_CORE_CONFIG_H

// -- Motor Driver 1 (Left Side) --
#define STBY_L      8

#define FL_IN1      2
#define FL_IN2      4
#define FL_PWM      9

#define RL_IN1      7
#define RL_IN2      12
#define RL_PWM      10

// -- Motor Driver 2 (Right Side) --
#define STBY_R      13

#define FR_IN1      A0  // D14
#define FR_IN2      A1  // D15
#define FR_PWM      5

#define RR_IN1      A2  // D16
#define RR_IN2      A3  // D17
#define RR_PWM      6

// -- Tuning and Constants --
#define PWM_MAX     255
#define WATCHDOG_MS 1000

// -- Motor Trims --
// Adjust these values to compensate for differences in motor speeds.
// Positive values increase the speed of the motor.
#define TRIM_FL     0
#define TRIM_FR     0
#define TRIM_RL     0
#define TRIM_RR     0

// -- Offsets --
// These are not changed unless the motor is physically mounted backwards.
#define OFFSET_FL   1
#define OFFSET_FR   1
#define OFFSET_RL   1
#define OFFSET_RR   1

#endif