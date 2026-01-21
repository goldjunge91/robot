#include "MecanumDriver.h"
#include <cmath>
#include <algorithm>

// Wenn wir nicht auf einem Arduino bauen, definieren wir einfache Stubs,
// damit sich der Code auf einem Host-Rechner testen lässt.
#ifndef ARDUINO
static void pinMode(int, int) {}
static void digitalWrite(int, int) {}
static void analogWrite(int, int) {}
static constexpr int OUTPUT = 0;
static constexpr int HIGH = 1;
static constexpr int LOW = 0;
#endif

MecanumDriver::MecanumDriver(const std::array<MotorPins,4>& pins, float max_rpm)
: pins_(pins), max_rpm_(max_rpm) {}

void MecanumDriver::begin() {
    for (auto &p : pins_) {
        pinMode(p.in1, OUTPUT);
        pinMode(p.in2, OUTPUT);
        pinMode(p.pwm, OUTPUT);
    }
}

void MecanumDriver::drive(float vx, float vy, float omega) {
    // Robotabmessungen in Metern
    const float L = 0.1f; // Länge
    const float W = 0.1f; // Breite
    const float r = 0.04f; // Radradius (40 mm)

    float wheel[4];
    wheel[0] = (vx - vy - (L+W) * omega) / r; // Front links
    wheel[1] = (vx + vy + (L+W) * omega) / r; // Front rechts
    wheel[2] = (vx + vy - (L+W) * omega) / r; // Heck links
    wheel[3] = (vx - vy + (L+W) * omega) / r; // Heck rechts

    float maxVal = 0.0f;
    for (float w : wheel) {
        maxVal = std::max(maxVal, std::fabs(w));
    }
    if (maxVal > max_rpm_) {
        for (float &w : wheel) {
            w = w / maxVal * max_rpm_;
        }
    }
    for (int i = 0; i < 4; ++i) {
        setMotor(i, wheel[i] / max_rpm_);
    }
}

void MecanumDriver::setMotor(int index, float value) {
    auto &p = pins_[index];
    bool forward = value >= 0;
    int pwm = static_cast<int>(std::min(1.0f, std::fabs(value)) * 255.0f);
    digitalWrite(p.in1, forward ? HIGH : LOW);
    digitalWrite(p.in2, forward ? LOW : HIGH);
    analogWrite(p.pwm, pwm);
}
