# Feature Specification: Omnidirectional ROS2 RC car with Nerf launcher

**Feature Branch**: `001-title-omnidirectional-ros2`  
**Created**: 2025-09-16  
**Status**: Draft  
**Input**: User description: "Omnidirectional ROS2 RC car robot with a Nerf dart launcher that can operate autonomously or be remote-controlled. Details are in Projekt.md"

## Execution Flow (main)

```text
1. Parse user description from Input
 -> If empty: ERROR "No feature description provided"
2. Extract key concepts from description
 -> Identify: actors, actions, data, constraints
3. For each unclear aspect:
 -> Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
 -> If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
 -> Each requirement must be testable
 -> Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
 -> If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
 -> If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines

- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

As a hobbyist/operator, I want an omnidirectional ROS2 robot with an integrated Nerf launcher so that it can autonomously navigate indoor environments, detect and aim at faces, and be manually driven via an Xbox controller when desired.

### Acceptance Scenarios

1. **Given** the robot is powered on and sensors initialized, **When** the operator requests autonomous mode, **Then** the robot starts SLAM-based localization and navigation, avoids obstacles, and can follow a high-level navigation command (e.g., go to goal) while reporting status to the dashboard.

2. **Given** the robot is in autonomous mode with camera feed active, **When** a human face is detected and the operator approves firing (or an allowed auto-fire policy is enabled), **Then** the turret aims at the detected face and fires a Nerf dart following safety checks (no obstruction, target within allowed range and angle).

3. **Given** the robot is in manual (teleop) mode, **When** the operator uses the Xbox controller, **Then** the robot responds to joystick inputs for omnidirectional movement and separate controls for turret pan/tilt and firing.

4. **Given** any sensor or critical system failure (battery low, sensor disconnect), **When** the failure is detected, **Then** the robot transitions to a safe state (stop motion, disable firing) and reports an error on the dashboard and local display.

### Edge Cases

- What happens when multiple faces are detected simultaneously? → Prioritize nearest or require operator selection.
- How does the system behave outdoors or in very bright/dim lighting? → Face detection performance may degrade; mark as constraint.
- What if the Nerf launcher jam occurs? → Detection via motor current spike (INA3221) or encoder feedback should trigger safe stop and report.
- How does SLAM handle dynamic obstacles (moving people)? → Planner must re-plan; safety -> stop if uncertain.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide omnidirectional locomotion controls (forward/backward, lateral, diagonal, rotation) via ROS2 topics/services for both autonomous and teleop modes.
- **FR-002**: The system MUST support autonomous SLAM-based mapping and localization using the onboard LiDAR and IMU, producing a 2D occupancy map and providing a localization pose on a ROS2 topic.
- **FR-003**: The system MUST provide a teleoperation interface accepting Xbox controller input and translating it to motor commands with configurable max speed and acceleration limits.
- **FR-004**: The system MUST fuse proximity data from the VL53L0X and LiDAR to detect and avoid nearby obstacles in real-time.
- **FR-005**: The system MUST stream camera frames over a ROS2 topic for computer-vision consumers (face detection node).
- **FR-006**: The system MUST detect human faces in the camera feed and publish target coordinates (pan/tilt angles and estimated range) for the turret controller.
- **FR-007**: The turret controller MUST accept target coordinates, aim the pan/tilt servos, and provide a status topic indicating aimed/locked state.
- **FR-008**: The firing action MUST require an explicit operator command OR follow a clearly defined, switchable auto-fire policy (modes: Automatic, Semi-automatic, Manual). Safety interlocks MUST prevent firing when conditions are unsafe. The controller MUST enforce a safety envelope: minimum shooting distance 1.0 m, maximum shooting distance 5.0 m, and turret tilt limited to -10° (down) .. +30° (up). The firing node MUST verify target range/angle before permitting a fire command.
- **FR-009**: The system MUST monitor battery voltage and current via INA3221 and publish alerts when battery state is below safe thresholds.
- **FR-010**: The system MUST provide a minimalist web dashboard accessible via browser on the same network that shows the live camera feed (first-person view), robot pose, battery status, sensor readings, emergency stop, current fire mode, and target-selection controls when operator-selection is active. The dashboard SHALL be implemented using existing ROS2 web tooling (rosbridge-suite for command/telemetry and web_video_server for video) or equivalent.
- **FR-011**: The low-level controller (Pico) MUST accept high-level velocity/steering commands over a defined serial/ROS bridge and produce motor PWM signals with closed-loop control using wheel encoder feedback.
- **FR-012**: The system MUST log mission events (mode changes, firing events, critical errors) with timestamps to local storage and optional dashboard retrieval.

*Ambiguities and clarifications are marked below where relevant.*

### Key Non-functional Requirements

- **NFR-001 (Safety)**: The system MUST prevent firing when human safety cannot be assured. System MUST include an emergency-stop that immediately disables motors and firing.
- **NFR-002 (Latency)**: Teleop control loop (controller input → motor command) SHOULD have <100 ms end-to-end latency.
- **NFR-003 (Runtime)**: The robot SHOULD operate for at least 30 minutes under nominal load on the provided battery pack.
- **NFR-004 (Accuracy)**: The turret aiming accuracy SHOULD be within ±5 degrees under nominal conditions.

### Key Entities *(include if feature involves data)*

- **RobotState**: current pose, velocity, battery status, mode (autonomous/manual), turret state, last error
- **Map**: 2D occupancy grid produced by SLAM, with metadata (timestamp, frame_id)
- **Target**: detected face with attributes {id, bounding_box, estimated_range, confidence, timestamp}
- **EventLog**: timestamped records of events (mode_change, fire, error, battery_alert)

---

## Review & Acceptance Checklist

### Content Quality

- [x] No implementation details that prescribe a specific language or framework (ROS2 is a platform constraint but acceptable as context)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

- ### Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Resolved clarifications (provided by stakeholder)

- Auto-fire policy: switchable modes supported — Automatic, Semi-automatic (operator confirmation), and Manual (no auto-fire). Mode selection is user-configurable and must be visible on the dashboard.
- Target selection: switchable behavior — selection by highest confidence OR operator choice. When operator choice is enabled, the dashboard must present detected targets for selection prior to firing.
- Safety envelope (enforced by firing controller):
  - Minimum shooting distance: 1.0 meter (prevent point-blank firing)
  - Maximum shooting distance: 5.0 meters
  - Tilt (vertical) limits: -10° (down) to +30° (up)
  - These limits together form a cone-shaped, front-facing safety envelope; the system MUST validate targets are inside this envelope before arming/firing.
- Map persistence and operating modes:
  - Two distinct operating modes: Mapping mode and Navigation mode.
  - Mapping mode: SLAM (e.g., `slam_toolbox`) runs; user explores and builds map. Map is saved only when the user triggers a manual save; persisted maps are stored as `.pgm` + `.yaml` files.
  - Navigation mode: `map_server` is used to load a stored map at startup in read-only mode; robot localizes against the loaded map and does not modify it at runtime.
  - Mode switching is a deliberate choice at startup (different launch configurations); dynamic switching during a mission is not supported by default.

These clarifications remove prior [NEEDS CLARIFICATION] markers in the spec.

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked and resolved
- [x] User scenarios defined
- [x] Requirements generated and updated
- [x] Entities identified
- [x] Review checklist passed

---

### Notes

- Source details taken from `Projekt.md` in repository root.
