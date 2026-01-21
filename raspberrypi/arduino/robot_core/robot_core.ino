/*
 * UNO + 2x TB6612 (SparkFun_TB6612) – Simple Serial Control für 4 Motoren
 * Befehle (mit '\n'):
 * V <L%> <R%>    : links/rechts in Prozent [-100..100]
 * STOP           : sofort stoppen/bremsen
 * PING           : "PONG"
 * VER?           : Versionsstring
 */

#include <SparkFun_TB6612.h>
#include <string.h>
#include <stdio.h>
#include "robot_core_config.h"

// ---------- Pins sind in robot_core_config.h definiert ----------

// Motorobjekte für 4 Motoren (2 pro Seite)
// Linke Seite
Motor motor1(L_AIN1, L_AIN2, L_PWMA, OFFSET_L1, L_STBY); // links, Motor 1
Motor motor2(L_BIN1, L_BIN2, L_PWMB, OFFSET_L2, L_STBY); // links, Motor 2
// Rechte Seite
Motor motor3(R_AIN1, R_AIN2, R_PWMA, OFFSET_R1, R_STBY); // rechts, Motor 3
Motor motor4(R_BIN1, R_BIN2, R_PWMB, OFFSET_R2, R_STBY); // rechts, Motor 4


// Laufzeit-Parameter
#define PWM_MAX     255
#define WATCHDOG_MS 2000   // stoppt, wenn so lange kein Kommando kam
unsigned long lastCmdMs = 0;

static inline int clamp255(int x){
  if (x >  PWM_MAX) return  PWM_MAX;
  if (x < -PWM_MAX) return -PWM_MAX;
  return x;
}

// Prozent [-100..100] → PWM [-255..255]
int pctToPwm(int pct){
  if (pct >  100) pct = 100;
  if (pct < -100) pct = -100;
  long v = (long)pct * PWM_MAX / 100;
  return (int)v;
}

void hardStop(){
  motor1.brake();
  motor2.brake();
  motor3.brake();
  motor4.brake();
}

void setup(){
  Serial.begin(115200);
  delay(1500);  // Auto-Reset abwarten
  lastCmdMs = millis();
  Serial.println(F("BOOT UNO_TB6612_4WD v1.1"));
}

void parseLine(char* line){
  // CR entfernen (falls CRLF)
  for (char* p=line; *p; ++p) if (*p=='\r') *p=0;
  if (!*line) return;

  if (strncmp(line, "V ", 2) == 0){
    int Lpct, Rpct;
    if (sscanf(line+2, "%d %d", &Lpct, &Rpct) == 2){
      // 1. Prozentwerte in Basis-PWM-Werte umrechnen
      int base_pwm_L = pctToPwm(Lpct);
      int base_pwm_R = pctToPwm(Rpct);

      // 2. Trim-Werte für jeden einzelnen Motor anwenden
      //    und anschließend auf den gültigen Bereich [-255, 255] begrenzen
      int final_L1 = clamp255(base_pwm_L + TRIM_L1);
      int final_L2 = clamp255(base_pwm_L + TRIM_L2);
      int final_R1 = clamp255(base_pwm_R + TRIM_R1);
      int final_R2 = clamp255(base_pwm_R + TRIM_R2);
      
      // 3. Alle vier Motoren ansteuern
      motor1.drive(final_L1); // Links 1
      motor2.drive(final_L2); // Links 2
      motor3.drive(final_R1); // Rechts 1 (als motor3 deklariert)
      motor4.drive(final_R2); // Rechts 2 (als motor4 deklariert)

      lastCmdMs = millis();
      Serial.print(F("ACK V ")); Serial.print(Lpct); Serial.print(' '); Serial.println(Rpct);
    } else {
      Serial.println(F("ERR V"));
    }
    return;
  }

  if (strcmp(line, "STOP") == 0){
    hardStop();
    lastCmdMs = millis();
    Serial.println(F("ACK STOP"));
    return;
  }

  if (strcmp(line, "PING") == 0){ Serial.println(F("PONG")); return; }
  if (strcmp(line, "VER?") == 0){ Serial.println(F("UNO_TB6612_4WD v1.1")); return; }

  Serial.println(F("ERR CMD"));
}

void loop(){
  // serielle Zeilen einlesen
  static char buf[48]; static uint8_t idx=0;
  while (Serial.available()){
    char c = Serial.read();
    if (c == '\n'){ buf[idx]=0; parseLine(buf); idx=0; }
    else if (idx < sizeof(buf)-1){ buf[idx++] = c; }
  }

  // Watchdog
  if (millis() - lastCmdMs > WATCHDOG_MS){
    hardStop();
    // kein lastCmdMs-Update -> bleibt gestoppt bis nächstes Kommando
  }
}

// /*
//  * UNO + TB6612 (SparkFun_TB6612) – Simple Serial Control
//  * Befehle (mit '\n'):
//  *   V <L%> <R%>    : links/rechts in Prozent [-100..100]
//  *   STOP           : sofort stoppen/bremsen
//  *   PING           : "PONG"
//  *   VER?           : Versionsstring
//  */

// #include <SparkFun_TB6612.h>
// #include <string.h>
// #include <stdio.h>
// #include "robot_core_config.h"
// // ---------- Pins (wie SparkFun Hookup Guide) ----------
// // #define AIN1 2
// // #define AIN2 4
// // #define PWMA 5   // PWM
// // #define BIN1 7
// // #define BIN2 8
// // #define PWMB 6   // PWM
// // #define STBY 9



// // Motorobjekte
// Motor motor1(L_AIN1, L_AIN2, L_PWMA, OFFSET_L1, L_STBY); // links
// Motor motor2(L_BIN1, L_BIN2, L_PWMB, OFFSET_L2, L_STBY); // links

// Motor motor3(R_AIN1, R_AIN2, R_PWMA, OFFSET_R1, R_STBY); // rechts
// Motor motor4(R_BIN1, R_BIN2, R_PWMB, OFFSET_R2, R_STBY); // rechts


// // Laufzeit-Parameter
// #define PWM_MAX     255
// #define WATCHDOG_MS 2000   // stoppt, wenn so lange kein Kommando kam
// unsigned long lastCmdMs = 0;

// static inline int clamp255(int x){
//   if (x >  PWM_MAX) return  PWM_MAX;
//   if (x < -PWM_MAX) return -PWM_MAX;
//   return x;
// }

// // Prozent [-100..100] → PWM [-255..255]
// int pctToPwm(int pct){
//   if (pct >  100) pct = 100;
//   if (pct < -100) pct = -100;
//   long v = (long)pct * PWM_MAX / 100;
//   return (int)v;
// }

// void hardStop(){
//   motor1.brake();
//   motor2.brake();
//   motor3.brake();
//   motor4.brake();
// }

// void setup(){
//   Serial.begin(115200);
//   delay(1500);  // Auto-Reset abwarten
//   lastCmdMs = millis();
//   Serial.println(F("BOOT UNO_TB6612 v1.0"));
// }

// void parseLine(char* line){
//   // CR entfernen (falls CRLF)
//   for (char* p=line; *p; ++p) if (*p=='\r') *p=0;
//   if (!*line) return;

//   if (strncmp(line, "V ", 2) == 0){
//     int Lpct, Rpct;
//     if (sscanf(line+2, "%d %d", &Lpct, &Rpct) == 2){
//       int L = clamp255(pctToPwm(Lpct));
//       int R = clamp255(pctToPwm(Rpct));
//       motor1.drive(L);
//       motor2.drive(R);
//       lastCmdMs = millis();
//       Serial.print(F("ACK V ")); Serial.print(Lpct); Serial.print(' '); Serial.println(Rpct);
//     } else {
//       Serial.println(F("ERR V"));
//     }
//     return;
//   }

//   if (strcmp(line, "STOP") == 0){
//     hardStop();
//     lastCmdMs = millis();
//     Serial.println(F("ACK STOP"));
//     return;
//   }

//   if (strcmp(line, "PING") == 0){ Serial.println(F("PONG")); return; }
//   if (strcmp(line, "VER?") == 0){ Serial.println(F("UNO_TB6612 v1.0")); return; }

//   Serial.println(F("ERR CMD"));
// }

// void loop(){
//   // serielle Zeilen einlesen
//   static char buf[48]; static uint8_t idx=0;
//   while (Serial.available()){
//     char c = Serial.read();
//     if (c == '\n'){ buf[idx]=0; parseLine(buf); idx=0; }
//     else if (idx < sizeof(buf)-1){ buf[idx++] = c; }
//   }

//   // Watchdog
//   if (millis() - lastCmdMs > WATCHDOG_MS){
//     hardStop();
//   //  lastCmdMs = millis(500); // 

//     // kein lastCmdMs-Update -> bleibt gestoppt bis nächstes Kommando
//   }
// }
