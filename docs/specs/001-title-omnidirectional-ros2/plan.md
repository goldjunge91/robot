---
description: "Implementation plan for an omnidirectional ROS 2 robot with a safety-governed Nerf launcher, SLAM/navigation, and a minimalist Next.js web dashboard."
scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

# Implementation Plan: Omnidirectional ROS2 RC car with Nerf launcher

**Branch**: `001-title-omnidirectional-ros2` | **Date**: 2025-09-16 | **Spec**: specs/001-title-omnidirectional-ros2/spec.md
**Input**: Feature specification from `specs/001-title-omnidirectional-ros2/spec.md`

## Execution Flow (/plan command scope)

```text
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

- Build an omnidirectional indoor robot (ROS 2 Humble) with SLAM/localization, teleop via Xbox controller, and a safety-governed Nerf launcher that can aim at detected faces. Minimalist web dashboard provides FPV video, status, estop, fire mode, and optional operator target selection. Two modes: Mapping (save maps manually) and Navigation (load map read-only). Firing safety envelope: distance 1.0–5.0 m, tilt −10°..+30°.
- Technical approach: All capabilities implemented as ROS 2 nodes with standard topics/services and launch files. Web dashboard uses rosbridge-suite and web_video_server; frontend scaffold planned with Next.js App Router but kept minimal and mobile-first.

## Technical Context

**Language/Version**: Python 3.10+ (rclpy), C++17 (rclcpp), TypeScript (Next.js App Router)  
**Primary Dependencies**: ROS 2 Humble (nav2, slam_toolbox, ros2_control), rosbridge_suite, web_video_server, OpenCV; Next.js App Router (minimal extras)  
**Storage**: Files on disk: maps as .pgm+.yaml under `src/robot/maps/` (per clarified naming); logs as plain text/JSON  
**Testing**: ament_pytest / ament_cmake_gtest; linters (flake8, ament_lint_auto); dashboard unit tests with Jest (lightweight)  
**Target Platform**: Ubuntu on Raspberry Pi 4B (robot), Windows/macOS/Linux dev; Gazebo sim  
**Project Type**: web (frontend + backend-like ROS graph)  
**Performance Goals**: Teleop loop <100 ms end-to-end; turret aim accuracy ±5°; stable 15–30 fps FPV stream  
**Constraints**: Minimal third-party web deps; safety envelope enforced before firing; launch files must run in sim and hardware  
**Scale/Scope**: Single robot, local network dashboard, single operator

## Constitution Check

Note: Must pass before Phase 0 research. Re-check after Phase 1 design.

Against `.specify/memory/constitution.md`:

- Buildable & Launchable: Use existing launch files (`launch_sim.launch.py`, `rsp.launch.py`, `launch_robot.launch.py`); ensure URDF/xacro parses and controllers spawn. PASS once plan artifacts reference current launches and quickstart includes commands.
- Minimal Tests: Add at least one ament test per package and run in CI. PENDING (to be added in Phase 1 outputs planning).
- Parameters over Hard-coding: Keep tunables in `config/*.yaml`; expose launch args (`use_sim_time`, `world`, controller YAML). PASS by design; verify during Phase 1 contracts.
- Code Quality Baseline: Enable ament linters; include in test plan. PENDING until tests/linters wired.
- Observability & Interfaces: Document topics/services/actions/TF frames in contracts; stabilize names. PENDING until contracts.md authored.
- Split High/Low Control and Safety: Firing envelope and watchdogs reflected in contracts and quickstart. PASS by requirement mapping.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```text
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (Web application). Rationale: ROS nodes act as backend; dashboard as frontend. Keep dependencies minimal; reuse rosbridge/web_video_server.

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts

Note: Prerequisite → research.md complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `{SCRIPT}` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach

Note: This section only describes what the /tasks command will do; do not execute during /plan.

**Task Generation Strategy**:

- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:

- TDD order: Tests before implementation
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

Note: These phases are beyond the scope of the /plan command.

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

Note: Fill ONLY if Constitution Check has violations that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Progress Tracking

Note: This checklist is updated during execution flow.

**Phase Status**:

- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
