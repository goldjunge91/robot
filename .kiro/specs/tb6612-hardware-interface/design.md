# Design Document

## Overview

The TB6612 Hardware Interface will be implemented as a new ROS 2 package in the `drive_arduino/` directory, following the DiffDriveArduino example structure. This C++ ros2_control hardware interface will replace the existing Python bridge and support three different drive configurations:

1. **4-Motor Normal Wheels** - Four independent motors with regular wheels
2. **Differential Drive** - Two motors with two normal wheels (left/right)
3. **Mecanum Drive** - Four motors with mecanum wheels using kinematic equations

The design maintains compatibility with the current Arduino firmware while implementing a clean separation between drive logic and serial communication, following the proven architectural patterns from the DiffDriveArduino example. The TB6612Comms class will handle all serial communication independently from the drive kinematics, allowing for modular and testable code.

## Architecture

### Package Structure

The `drive_arduino/` package will follow the same directory structure as the DiffDriveArduino example:

```
drive_arduino/
├── CMakeLists.txt              # Build configuration with serial library dependency
├── package.xml                 # Package metadata and dependencies
├── include/tb6612_hardware/    # Header files
│   ├── tb6612_hardware.hpp     # Main hardware interface class
│   ├── tb6612_comms.hpp        # Serial communication class
│   └── config.hpp              # Configuration structures
├── src/                        # Source files
│   ├── tb6612_hardware.cpp     # Hardware interface implementation
│   └── tb6612_comms.cpp        # Communication implementation
├── controllers/                # Controller configuration files
│   ├── tb6612_controllers.yaml # Example controller configs
│   └── ...
├── launch/                     # Launch files
│   ├── tb6612_hardware.launch.py
│   └── ...
└── tb6612_hardware.xml         # Plugin description file
```

### Class Structure

The implementation will consist of three main components, following the DiffDriveArduino architectural pattern:

1. **TB6612HardwareInterface** - Main hardware interface class implementing `hardware_interface::SystemInterface` (similar to DiffDriveArduino)
2. **TB6612Comms** - Serial communication class (adapted from ArduinoComms in DiffDriveArduino)
3. **Config** - Configuration structure for parameters (extended from DiffDriveArduino Config)

### Integration Points

- **ros2_control framework** - Provides the base SystemInterface and hardware interface types
- **Serial library** - Uses the existing `serial/` library for communication (same as DiffDriveArduino)
- **Controller Manager** - Integrates with standard ros2_control controllers
- **Pluginlib** - Registered as a plugin for dynamic loading
- **DiffDriveArduino structure** - Follows the same package organization and class architecture patterns

## Components and Interfaces

### TB6612HardwareInterface Class

```cpp
class TB6612HardwareInterface : public hardware_interface::BaseInterface<hardware_interface::SystemInterface>
{
public:
  TB6612HardwareInterface();
  
  // Hardware Interface Methods
  return_type configure(const hardware_interface::HardwareInfo & info) override;
  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;
  return_type start() override;
  return_type stop() override;
  return_type read() override;
  return_type write() override;

private:
  Config cfg_;
  TB6612Comms tb6612_;
  Wheel l_wheel_;
  Wheel r_wheel_;
  rclcpp::Logger logger_;
  std::chrono::time_point<std::chrono::system_clock> time_;
};
```

### TB6612Comms Class

Adapted from ArduinoComms but modified for TB6612 protocol with multi-motor support and optional encoder feedback:

```cpp
class TB6612Comms
{
public:
  TB6612Comms();
  TB6612Comms(const std::string &serial_device, int32_t baud_rate, int32_t timeout_ms);
  
  void setup(const std::string &serial_device, int32_t baud_rate, int32_t timeout_ms);
  void sendPing();  // Sends "PING\n" for Arduino reset sync
  
  // Motor command methods for different drive types
  void setDifferentialMotors(int left_val, int right_val);  // "V {left} {right}\n"
  void setFourMotors(int fl, int fr, int rl, int rr);       // "M {fl} {fr} {rl} {rr}\n"
  
  // Encoder reading methods (optional)
  void readDifferentialEncoders(int &left_enc, int &right_enc);     // "E\n" -> "left right"
  void readFourEncoders(int &fl, int &fr, int &rl, int &rr);        // "E\n" -> "fl fr rl rr"
  
  bool connected() const;
  
private:
  serial::Serial serial_conn_;
  std::string findSerialPort(const std::string &preferred_port);
  void sendMsg(const std::string &msg);
  std::string sendMsgWithResponse(const std::string &msg);
};
```

### Configuration Structure

Extended from the existing Config to include TB6612-specific parameters and drive type support:

```cpp
enum class DriveType {
  DIFFERENTIAL,    // 2 motors, differential drive
  FOUR_WHEEL,      // 4 motors, independent control
  MECANUM          // 4 motors, mecanum kinematics
};

struct Config
{
  // Drive configuration
  DriveType drive_type = DriveType::DIFFERENTIAL;
  bool has_encoders = false;  // Whether the setup includes encoders
  
  // Wheel names (varies by drive type)
  std::string left_wheel_name = "left_wheel";
  std::string right_wheel_name = "right_wheel";
  std::string front_left_wheel_name = "front_left_wheel";
  std::string front_right_wheel_name = "front_right_wheel";
  std::string rear_left_wheel_name = "rear_left_wheel";
  std::string rear_right_wheel_name = "rear_right_wheel";
  
  // Communication parameters
  float loop_rate = 20.0;
  std::string device = "";
  int baud_rate = 115200;
  int timeout = 50;
  
  // Velocity limits
  float max_lin_vel = 0.3;  // m/s
  float max_ang_vel = 1.0;  // rad/s
  
  // Drive-specific parameters
  float mix_factor = 0.5;   // For differential drive
  float wheel_base = 0.3;   // L - distance between front and rear axles (mecanum)
  float track_width = 0.3;  // W - distance between left and right wheels (mecanum)
  
  // Encoder parameters (only used if has_encoders = true)
  int enc_counts_per_rev = 1920;
  float wheel_radius = 0.05;  // meters
};
```

## Data Models

### State Interfaces

**Differential Drive (2 wheels):**
- `left_wheel_joint/velocity` - Left wheel velocity (rad/s)
- `left_wheel_joint/position` - Left wheel position (rad)
- `right_wheel_joint/velocity` - Right wheel velocity (rad/s)  
- `right_wheel_joint/position` - Right wheel position (rad)

**Four Wheel / Mecanum Drive (4 wheels):**
- `front_left_wheel_joint/velocity` - Front left wheel velocity (rad/s)
- `front_left_wheel_joint/position` - Front left wheel position (rad)
- `front_right_wheel_joint/velocity` - Front right wheel velocity (rad/s)
- `front_right_wheel_joint/position` - Front right wheel position (rad)
- `rear_left_wheel_joint/velocity` - Rear left wheel velocity (rad/s)
- `rear_left_wheel_joint/position` - Rear left wheel position (rad)
- `rear_right_wheel_joint/velocity` - Rear right wheel velocity (rad/s)
- `rear_right_wheel_joint/position` - Rear right wheel position (rad)

### Command Interfaces

**Differential Drive:**
- `left_wheel_joint/velocity` - Left wheel velocity command (rad/s)
- `right_wheel_joint/velocity` - Right wheel velocity command (rad/s)

**Four Wheel / Mecanum Drive:**
- `front_left_wheel_joint/velocity` - Front left wheel velocity command (rad/s)
- `front_right_wheel_joint/velocity` - Front right wheel velocity command (rad/s)
- `rear_left_wheel_joint/velocity` - Rear left wheel velocity command (rad/s)
- `rear_right_wheel_joint/velocity` - Rear right wheel velocity command (rad/s)

### Communication Protocol

**Differential Drive Commands:**
- Format: `"V {left_value} {right_value}\n"`
- Values: Integer range -100 to 100

**Four Motor Commands:**
- Format: `"M {fl} {fr} {rl} {rr}\n"`
- Values: Integer range -100 to 100
- Order: Front-Left, Front-Right, Rear-Left, Rear-Right

**Encoder Reading (if has_encoders = true):**
- Differential: `"E\n"` -> Response: `"{left_count} {right_count}\n"`
- Four Motor: `"E\n"` -> Response: `"{fl_count} {fr_count} {rl_count} {rr_count}\n"`

**Initialization:**
- Send `"PING\n"` on connection for Arduino reset synchronization
- Wait 2 seconds after connection (matching Python behavior)

**Value Conversion:**
- Motor commands: `cmd_value = clamp(wheel_vel_cmd / max_vel * 100, -100, 100)`
- Encoder feedback: `wheel_angle = (encoder_count / enc_counts_per_rev) * 2 * PI`

## Error Handling

### Serial Communication Errors
- **Connection Failure**: Return `return_type::ERROR` from configure()
- **Write Failure**: Log error, continue operation, return `return_type::ERROR` from write()
- **Port Detection**: Try candidate ports in order, fail if none available

### Parameter Validation
- **Invalid Parameters**: Log warnings, use default values
- **Missing Required Parameters**: Use sensible defaults based on Python implementation

### Runtime Errors
- **Lost Connection**: Detect in write() method, attempt reconnection
- **Invalid Commands**: Clamp values to valid ranges

## Testing Strategy

### Unit Tests
1. **TB6612Comms Tests**
   - Serial port detection logic
   - Message formatting and sending
   - Connection handling and error cases

2. **TB6612HardwareInterface Tests**
   - Configuration parameter parsing
   - State/command interface export
   - Velocity command conversion and clamping

### Integration Tests
1. **Hardware Interface Loading**
   - Plugin registration and discovery
   - Controller manager integration
   - Parameter loading from YAML

2. **Communication Protocol**
   - Mock serial device testing
   - Command format validation
   - Error handling scenarios

### System Tests
1. **End-to-End Testing**
   - Integration with diff_drive_controller
   - Launch file compatibility
   - Real hardware communication (if available)

## Implementation Notes

### Serial Port Auto-Detection
The implementation will replicate the Python bridge's port detection logic:
```cpp
const std::vector<std::string> CANDIDATES = {
    // Sorted glob results from /dev/serial/by-id/*
    "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"
};
```

### Velocity Conversion
Commands will be converted from rad/s to TB6612 values using the same logic as the Python bridge:
```cpp
int convertVelocityCommand(double wheel_vel_rad_s, double max_vel) {
    double normalized = wheel_vel_rad_s / max_vel;
    return static_cast<int>(std::round(100.0 * std::clamp(normalized, -1.0, 1.0)));
}
```

### Mecanum Drive Kinematics

For mecanum drive configuration, the hardware interface will implement inverse kinematics to convert Twist commands to individual wheel velocities:

```cpp
// Mecanum inverse kinematics
// Input: vx (m/s), vy (m/s), omega (rad/s)
// Output: wheel velocities (rad/s)

double L = cfg_.wheel_base;   // Distance between front and rear axles
double W = cfg_.track_width;  // Distance between left and right wheels

double fl_vel = vx - vy - (L + W) * omega;
double fr_vel = vx + vy + (L + W) * omega;
double rl_vel = vx + vy - (L + W) * omega;
double rr_vel = vx - vy + (L + W) * omega;
```

### Drive Type Selection

The hardware interface will determine the drive type from configuration and export the appropriate number of interfaces:

- **DIFFERENTIAL**: 2 wheels (left/right)
- **FOUR_WHEEL**: 4 wheels (independent control)
- **MECANUM**: 4 wheels (mecanum kinematics)

### State Integration

**With Encoders (has_encoders = true):**
- Position: Read from encoder counts and convert to radians
- Velocity: Calculate from position change over time delta
- Similar to DiffDriveArduino implementation

**Without Encoders (has_encoders = false):**
- Position: Integrate from velocity commands over time
- Velocity: Set directly from velocity commands
- Similar to FakeRobot implementation

### Plugin Registration
The hardware interface will be registered via pluginlib with an XML description file similar to `fake_robot_hardware.xml`.