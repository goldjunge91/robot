#include "MecanumDriver.h"
#include <array>

int main() {
    std::array<MotorPins,4> pins{ {
        {1,2,3},  // Front links
        {4,5,6},  // Front rechts
        {7,8,9},  // Heck links
        {10,11,12} // Heck rechts
    } };

    MecanumDriver driver(pins, 100.0f);
    driver.begin();
    // Fahren nach vorne mit 0.5 m/s
    driver.drive(0.5f, 0.0f, 0.0f);
    // Rotation im Uhrzeigersinn
    driver.drive(0.0f, 0.0f, -0.5f);
    return 0;
}
