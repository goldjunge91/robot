#pragma once
#include <array>

struct MotorPins {
    int in1;
    int in2;
    int pwm;
};

class MecanumDriver {
public:
    explicit MecanumDriver(const std::array<MotorPins,4>& pins, float max_rpm = 100.0f);
    void begin();
    void drive(float vx, float vy, float omega);
private:
    std::array<MotorPins,4> pins_;
    float max_rpm_;
    void setMotor(int index, float value);
};
