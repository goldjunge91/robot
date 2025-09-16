// Raspberry Pi Pico (RP2040) - Arduino C++ firmware
// 4 Motors (TB6612), 4 Encoders, 2 ESCs, 1 CR-Servo (gear)
// Uses SparkFun_TB6612 and a config header similar to robot_core_config.h

#include <Arduino.h>
#include <SparkFun_TB6612.h>
#include <Servo.h>

// Bring in pin config and tuning macros (same style as robot_core_config.h)
#include "/robot_core_config.h"


// ======= Timing/Config =======
static const uint32_t MOTOR_PWM_FREQ = 10000;  // 10 kHz (quiet-ish)
static const uint16_t PWM_RANGE = PWM_MAX;     // align with SparkFun drive range

static const int SERVO_MIN_US = 1000;
static const int SERVO_CENTER_US = 1500;
static const int SERVO_MAX_US = 2000;

// Gear (CR servo)
static int one_rev_ms = 2200;      // ms for approx. one rotation
static int gear_speed_percent = 60; // 0..100
static int default_speed = 50;      // WASD default (0..100)

// ======= Encoder state =======
struct Enc {
  uint8_t a;
  uint8_t b;
  volatile int32_t cnt;
  uint8_t last;
};

static Enc ENCS[4] = {
  {ENC_FL_A, ENC_FL_B, 0, 0},
  {ENC_FR_A, ENC_FR_B, 0, 0},
  {ENC_RL_A, ENC_RL_B, 0, 0},
  {ENC_RR_A, ENC_RR_B, 0, 0},
};

// 4x quadrature decode LUT
static const int8_t QDEC_LUT[16] = {0,-1, 1,0,  1,0,0,-1,  -1,0,0,1,  0,1,-1,0};

// Forward declarations
static void enc_handle(uint8_t idx);
static void isr_fl_a(); static void isr_fl_b();
static void isr_fr_a(); static void isr_fr_b();
static void isr_rl_a(); static void isr_rl_b();
static void isr_rr_a(); static void isr_rr_b();

// ======= Motor control (SparkFun_TB6612) =======
Motor motorFL(FL_IN1, FL_IN2, FL_PWM, OFFSET_FL, STBY_L);
Motor motorRL(RL_IN1, RL_IN2, RL_PWM, OFFSET_RL, STBY_L);
Motor motorFR(FR_IN1, FR_IN2, FR_PWM, OFFSET_FR, STBY_R);
Motor motorRR(RR_IN1, RR_IN2, RR_PWM, OFFSET_RR, STBY_R);

static inline int clampPwm(int x) { return constrain(x, -PWM_MAX, PWM_MAX); }
static inline int pctToPwm(int pct) { return (int)((long)constrain(pct, -100, 100) * PWM_MAX / 100L); }

static void motor_set(int i, int speed_pct) {
  int pwm = pctToPwm(speed_pct);
  switch (i) {
    case 0: motorFL.drive(clampPwm(pwm + TRIM_FL)); break;
    case 1: motorFR.drive(clampPwm(pwm + TRIM_FR)); break;
    case 2: motorRL.drive(clampPwm(pwm + TRIM_RL)); break;
    case 3: motorRR.drive(clampPwm(pwm + TRIM_RR)); break;
    default: break;
  }
}

static void motors_stop() {
  motorFL.brake();
  motorFR.brake();
  motorRL.brake();
  motorRR.brake();
}

// ======= ESC/Servo =======
Servo esc1, esc2, gear;

static inline int clampi(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }

static void esc_throttle_percent(Servo &esc, int pct) {
  pct = clampi(pct, 0, 100);
  int us = SERVO_MIN_US + (SERVO_MAX_US - SERVO_MIN_US) * pct / 100;
  esc.writeMicroseconds(us);
}

static void gear_speed_percent_fn(int pct) {
  pct = clampi(pct, -100, 100);
  int span = (SERVO_MAX_US - SERVO_MIN_US) / 2; // ±500us
  int us = SERVO_CENTER_US + (span * pct) / 100;
  gear.writeMicroseconds(us);
}

static void gear_one_rotation(bool cw) {
  int spd = cw ? gear_speed_percent : -gear_speed_percent;
  gear_speed_percent_fn(spd);
  delay(one_rev_ms);
  gear.writeMicroseconds(SERVO_CENTER_US);
  Serial.print("[OK] Zahnrad: 1 Umdrehung ");
  Serial.print(cw ? "CW" : "CCW");
  Serial.println('.');
}

// ======= Mecanum mixing =======
static void mecanum(int vx, int vy, int wz) { // inputs -100..100
  int fl = vx + vy + wz;
  int fr = vx - vy - wz;
  int rl = vx - vy + wz;
  int rr = vx + vy - wz;
  int m = max(1, max(max(abs(fl), abs(fr)), max(abs(rl), abs(rr))));
  motor_set(0, (fl * 100) / m);
  motor_set(1, (fr * 100) / m);
  motor_set(2, (rl * 100) / m);
  motor_set(3, (rr * 100) / m);
}

// ======= Encoder IRQs =======
static void enc_handle(uint8_t idx) {
  Enc &e = ENCS[idx];
  uint8_t a = digitalRead(e.a);
  uint8_t b = digitalRead(e.b);
  uint8_t cur = (a << 1) | b;
  uint8_t lut_idx = ((e.last & 0x3) << 2) | (cur & 0x3);
  e.cnt += QDEC_LUT[lut_idx];
  e.last = cur;
}

static void isr_fl_a(){ enc_handle(0);} static void isr_fl_b(){ enc_handle(0);} 
static void isr_fr_a(){ enc_handle(1);} static void isr_fr_b(){ enc_handle(1);} 
static void isr_rl_a(){ enc_handle(2);} static void isr_rl_b(){ enc_handle(2);} 
static void isr_rr_a(){ enc_handle(3);} static void isr_rr_b(){ enc_handle(3);} 

// ======= CLI helpers =======
static String readLine() {
  static String buf;
  while (Serial.available()) {
    int c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') { String out = buf; buf = ""; return out; }
    if (buf.length() < 128) buf += (char)c;
  }
  return String();
}

static void print_help() {
  Serial.println(F(
    "\nBefehle:\n"
    "  arm                      - ESCs armen (3s Min-Gas)\n"
    "  esc1 <0-100>             - ESC1 auf Prozent\n"
    "  esc2 <0-100>             - ESC2 auf Prozent\n"
    "  both <0-100>             - beide ESCs gleich setzen\n"
    "  stop                     - beide ESCs auf 0% und Zahnrad stop\n"
    "  gear                     - Zahnrad 1 Umdrehung CW\n"
    "  gearccw                  - Zahnrad 1 Umdrehung CCW\n"
    "  setrev <ms>              - Dauer für 1 Umdrehung\n"
    "  gearspeed <0-100>        - Drehgeschwindigkeit Zahnrad\n"
    "  pulse <dev> <us>         - Rohpuls: dev=esc1|esc2|gear, us=1000..2000\n"
    "  enc                      - Zeigt Encoder-Zähler [FL,FR,RL,RR]\n"
    "  enc reset                - Setzt Encoder-Zähler 0\n"
    "  enctest <idx> [ms]       - Delta für Rad idx (0..3)\n"
    "\n  WASD-Bewegung:\n"
    "  w/a/s/d/q/e [speed]      - vor/links/zurück/rechts/rot links/rot rechts\n"
    "  x                        - stop\n"
    "  motortest <i> <pct> <ms> - Einzelmotor test\n"
    "  speed [val]              - Zeigt/Setzt default_speed\n"
    "  help                     - Hilfe\n"));
}

// ======= Setup =======
void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  // PWM config omitted for Arduino mbed_rp2040 core (uses default analogWrite)

  // Encoders
  const uint8_t encPins[] = {
    ENC_FL_A,ENC_FL_B, ENC_FR_A,ENC_FR_B, ENC_RL_A,ENC_RL_B, ENC_RR_A,ENC_RR_B
  };
  for (uint8_t p : encPins) pinMode(p, INPUT_PULLUP);
  for (int i = 0; i < 4; ++i) {
    ENCS[i].last = (digitalRead(ENCS[i].a) << 1) | digitalRead(ENCS[i].b);
  }
  attachInterrupt(digitalPinToInterrupt(ENC_FL_A), isr_fl_a, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_FL_B), isr_fl_b, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_FR_A), isr_fr_a, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_FR_B), isr_fr_b, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_RL_A), isr_rl_a, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_RL_B), isr_rl_b, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_RR_A), isr_rr_a, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_RR_B), isr_rr_b, CHANGE);

  // ESCs / Gear
  esc1.attach(ESC1_PIN);
  esc2.attach(ESC2_PIN);
  gear.attach(GEAR_PIN);
  esc_throttle_percent(esc1, 0);
  esc_throttle_percent(esc2, 0);
  gear.writeMicroseconds(SERVO_CENTER_US);

  Serial.println("=== Pico C++ Motor/ESC Terminal (SparkFun_TB6612) ===");
  Serial.println("[INFO] Using robot_core_config.h for pins and tuning");
  print_help();
}

// ======= Loop / CLI =======
void loop() {
  String line = readLine();
  if (line.length() == 0) { delay(5); return; }
  line.trim();
  if (line.length() == 0) return;

  // Parse
  // Simple split by spaces
  const int MAXTOK = 5;
  String tok[MAXTOK]; int ntok = 0;
  int start = 0;
  while (start < line.length() && ntok < MAXTOK) {
    int sp = line.indexOf(' ', start);
    if (sp < 0) sp = line.length();
    tok[ntok++] = line.substring(start, sp);
    start = sp + 1;
    while (start < line.length() && line[start] == ' ') start++;
  }
  tok[0].toLowerCase();

  auto getInt = [&](int i, int def=0){ return (i < ntok) ? tok[i].toInt() : def; };

  if (tok[0] == "help") {
    print_help();
  } else if (tok[0] == "arm") {
    esc_throttle_percent(esc1, 0);
    esc_throttle_percent(esc2, 0);
    delay(3000);
    Serial.println("[OK] Arming abgeschlossen.");
  } else if (tok[0] == "esc1" && ntok >= 2) {
    esc_throttle_percent(esc1, clampi(getInt(1),0,100));
  } else if (tok[0] == "esc2" && ntok >= 2) {
    esc_throttle_percent(esc2, clampi(getInt(1),0,100));
  } else if (tok[0] == "both" && ntok >= 2) {
    int p = clampi(getInt(1),0,100);
    esc_throttle_percent(esc1, p);
    esc_throttle_percent(esc2, p);
  } else if (tok[0] == "stop") {
    esc_throttle_percent(esc1, 0);
    esc_throttle_percent(esc2, 0);
    gear.writeMicroseconds(SERVO_CENTER_US);
    motors_stop();
    Serial.println("[OK] Alles gestoppt.");
  } else if (tok[0] == "gear") {
    gear_one_rotation(true);
  } else if (tok[0] == "gearccw") {
    gear_one_rotation(false);
  } else if (tok[0] == "setrev" && ntok >= 2) {
    one_rev_ms = max(100, getInt(1));
    Serial.print("[OK] one_rev_ms = "); Serial.print(one_rev_ms); Serial.println(" ms");
  } else if (tok[0] == "gearspeed" && ntok >= 2) {
    gear_speed_percent = clampi(getInt(1), 0, 100);
    Serial.print("[OK] gear_speed_percent = "); Serial.print(gear_speed_percent); Serial.println('%');
  } else if (tok[0] == "pulse" && ntok >= 3) {
    String dev = tok[1]; dev.toLowerCase();
    int us = clampi(getInt(2), SERVO_MIN_US, SERVO_MAX_US);
    bool handled = false;
    if (dev == "esc1") { esc1.writeMicroseconds(us); handled = true; }
    else if (dev == "esc2") { esc2.writeMicroseconds(us); handled = true; }
    else if (dev == "gear") { gear.writeMicroseconds(us); handled = true; }
    if (handled) { Serial.print("[OK] "); Serial.print(dev); Serial.print(" <- "); Serial.print(us); Serial.println("us"); }
    else Serial.println("[ERR] Unbekanntes Gerät (esc1|esc2|gear).");
  } else if (tok[0] == "enc") {
    if (ntok >= 2 && (tok[1] == "reset" || tok[1] == "zero" || tok[1] == "clear")) {
      noInterrupts(); for (int i=0;i<4;++i) ENCS[i].cnt = 0; interrupts();
      Serial.println("[OK] Encoder-Zähler zurückgesetzt.");
    } else {
      noInterrupts(); int32_t v0=ENCS[0].cnt,v1=ENCS[1].cnt,v2=ENCS[2].cnt,v3=ENCS[3].cnt; interrupts();
      Serial.print("[INFO] Encoder counts (FL,FR,RL,RR): [");
      Serial.print(v0); Serial.print(','); Serial.print(v1); Serial.print(','); Serial.print(v2); Serial.print(','); Serial.print(v3); Serial.println(']');
    }
  } else if (tok[0] == "enctest" && ntok >= 2) {
    int idx = clampi(getInt(1), 0, 3);
    int ms = (ntok >= 3) ? getInt(2) : 1000;
    noInterrupts(); int32_t s0=ENCS[0].cnt,s1=ENCS[1].cnt,s2=ENCS[2].cnt,s3=ENCS[3].cnt; interrupts();
    delay(ms);
    noInterrupts(); int32_t e0=ENCS[0].cnt,e1=ENCS[1].cnt,e2=ENCS[2].cnt,e3=ENCS[3].cnt; interrupts();
    int32_t d[4] = {e0-s0, e1-s1, e2-s2, e3-s3};
    Serial.print("[OK] enctest idx="); Serial.print(idx);
    Serial.print(" over "); Serial.print(ms); Serial.print("ms -> delta="); Serial.print(d[idx]);
    Serial.print(", all=["); Serial.print(d[0]); Serial.print(','); Serial.print(d[1]); Serial.print(','); Serial.print(d[2]); Serial.print(','); Serial.print(d[3]); Serial.println(']');
  } else if (tok[0] == "w") {
    int spd = (ntok>=2)? clampi(getInt(1),0,100) : default_speed; default_speed = spd;
    mecanum(spd, 0, 0);
    Serial.print("[OK] Moving forward at "); Serial.print(spd); Serial.println('%');
  } else if (tok[0] == "s") {
    int spd = (ntok>=2)? clampi(getInt(1),0,100) : default_speed; default_speed = spd;
    mecanum(-spd, 0, 0);
    Serial.print("[OK] Moving backward at "); Serial.print(spd); Serial.println('%');
  } else if (tok[0] == "a") {
    int spd = (ntok>=2)? clampi(getInt(1),0,100) : default_speed; default_speed = spd;
    mecanum(0, -spd, 0);
    Serial.print("[OK] Strafing left at "); Serial.print(spd); Serial.println('%');
  } else if (tok[0] == "d") {
    int spd = (ntok>=2)? clampi(getInt(1),0,100) : default_speed; default_speed = spd;
    mecanum(0, spd, 0);
    Serial.print("[OK] Strafing right at "); Serial.print(spd); Serial.println('%');
  } else if (tok[0] == "q") {
    int spd = (ntok>=2)? clampi(getInt(1),0,100) : default_speed; default_speed = spd;
    mecanum(0, 0, -spd);
    Serial.print("[OK] Turning left at "); Serial.print(spd); Serial.println('%');
  } else if (tok[0] == "e") {
    int spd = (ntok>=2)? clampi(getInt(1),0,100) : default_speed; default_speed = spd;
    mecanum(0, 0, spd);
    Serial.print("[OK] Turning right at "); Serial.print(spd); Serial.println('%');
  } else if (tok[0] == "x") {
    motors_stop();
    Serial.println("[OK] All motors stopped");
  } else if (tok[0] == "speed") {
    if (ntok >= 2) { default_speed = clampi(getInt(1),0,100); Serial.print("[OK] default_speed set to "); Serial.print(default_speed); Serial.println('%'); }
    else { Serial.print("[INFO] default_speed = "); Serial.print(default_speed); Serial.println('%'); }
  } else if (tok[0] == "motortest" && ntok >= 4) {
    int idx = clampi(getInt(1),0,3); int pct = clampi(getInt(2),-100,100); int ms = getInt(3);
    Serial.print("[OK] Test motor "); Serial.print(idx); Serial.print(" @ "); Serial.print(pct); Serial.print("% für "); Serial.print(ms); Serial.println("ms");
    motor_set(idx, pct); delay(ms); motor_set(idx, 0);
  } else {
    Serial.println("[ERR] Unbekannter Befehl. 'help' für Übersicht.");
  }
}
