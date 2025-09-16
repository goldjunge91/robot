# Tasks: Omnidirectional ROS2 RC car with Nerf launcher

Input: Design documents from `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/specs/001-title-omnidirectional-ros2/`
Prerequisites: plan.md (required), research.md, data-model.md, contracts/

## Phase 3.1: Setup

- [x] T001 Create maps directory `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/maps/` and document naming in README
- [x] T002 Initialize testing and linting: add ament_pytest for Python nodes/tests; ament_lint_auto for C++; configure flake8/black in package where applicable
- [x] T003 [P] Add CI-friendly instructions to `README.md` for build (`colcon build`), tests (`colcon test`), and lint
- [x] T004 Configure rosbridge_suite and web_video_server launch entries or instructions for dashboard bring-up

## Phase 3.2: Tests First (TDD)

- [ ] T005 [P] Contract tests for ROS interfaces in `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/test/contract/test_topics.py` asserting presence/types:
      - /mecanum_drive_controller/reference_unstamped (geometry_msgs/Twist)
      - /joint_states, /tf, /tf_static
      - /camera/image_raw, /scan, /imu, /range/front
      - /map, /map_metadata, localization pose topic
- [ ] T006 [P] Contract tests for launcher safety in `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/test/contract/test_launcher_safety.py` covering arm requirement and envelope (1.0–5.0 m, −10°..+30°)
- [ ] T007 [P] Contract tests for dashboard bridge in `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/test/contract/test_rosbridge_video.py` ensuring rosbridge WS reachable and video stream topic available
- [ ] T008 Integration test: simulation bring-up in `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/test/integration/test_sim_launch.py` spawning controllers and verifying `/joint_states` traffic and `odom->base_link` TF
- [ ] T009 Integration test: mapping workflow in `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/test/integration/test_mapping_flow.py` (stub) verifying map topics and save call placeholder
- [ ] T010 Integration test: navigation workflow in `C:/Users/tozzi/Desktop/rc/dev_ws_robot/src/robot/test/integration/test_navigation_flow.py` (stub) verifying map loaded and NavigateToPose action server available

## Phase 3.3: Core Implementation

- [ ] T011 [P] Define Target message schema draft in `specs/001-title-omnidirectional-ros2/contracts/` (or select existing msg) and align topics in launch/README
- [ ] T012 [P] Implement launcher safety node (rclpy) skeleton in `src/` reading target + range/angle, enforcing arm + envelope before publishing `/fire/cmd`
- [ ] T013 [P] Implement face detection node (rclpy) skeleton to publish `/target/detections`
- [ ] T014 Wire mecanum controller topics per config: confirm publish to `/mecanum_drive_controller/reference_unstamped` in sim and HW paths
- [ ] T015 Add rosbridge and web_video_server launch snippets or separate launch file under `launch/`

## Phase 3.4: Integration

- [ ] T016 Connect TB6612 Pico bridge robustly in `launch_robot.launch.py` (enable or document external launch) and verify parameters in `config/tb6612_bridge.yaml`
- [ ] T017 Add battery/diagnostics publisher skeleton and topics mapping to `sensor_msgs/BatteryState` and `diagnostic_msgs`
- [ ] T018 Update `README.md` with topic table from `contracts/topics-and-services.md` and quickstart steps

## Phase 3.5: Polish

- [ ] T019 [P] Unit tests for launcher safety node (range/angle edge cases)
- [ ] T020 [P] Unit tests for face detection node (publishes on detection; handles no-face)
- [ ] T021 Performance pass: ensure teleop latency target; reduce video resolution if needed
- [ ] T022 Docs tidy-up: cross-link spec, plan, research, quickstart; add map naming conventions
- [ ] T023 Final lint/test/launch smoke validation and checklist update in plan.md

## Dependencies

- Setup (T001-T004) before Tests (T005-T010)
- Tests before Core (T011–T015)
- Core before Integration (T016–T018)
- Everything before Polish (T019–T023)
- Parallel [P] tasks target different files (no shared edits)

## Parallel Execution Examples

- Group 1 [P]: T003, T005, T006, T007
- Group 2 [P]: T011, T012, T013
- Group 3 [P]: T019, T020

Notes:

- Contract tests assert presence and type only initially (will fail until nodes/launch added)
- Integration tests can use timeouts and topic discovery
- Keep topics aligned with `config/my_controllers_mecanum.yaml` and launch files