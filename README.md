Bruce‑Constraint‑Aware‑Decision‑Module (BCADM)
BCADM provides a contract‑aware, multi‑constraint decision loop designed for robotics safety workflows.
It evaluates system state, applies constraint boundaries, triggers clamping when needed, and produces structured, interpretable action‑contract logs suitable for real robotics models, simulators, and teaching environments.

BCADM now incorporates OmniLink’s safety‑layer recommendations:

Multi‑constraint reporting

violated_rules lists all fired constraints

violated_rule preserves backward‑compatible “last rule wins”

Intervention semantics

intervention_time is stamped only when a true intervention occurs (modified == True)

Branchable recovery state

recovery_state reports safe, status, and clamped_axes

Contract activation in normal operation

The decision loop blends structural stability with boundary‑seeking behavior, ensuring constraints are exercised naturally

Perfect for:

supervisory safety layers

humanoid robot stability envelopes

safe‑mode controllers

mobile robot navigation

drone geofence/tilt‑limit testing

ROS2 research environments

constraint‑aware teaching toolsExample Usage
yaml
name: BCADM Decision
uses: Bruce/BCADM@v1
with:
  state: "battery_low"
  constraints: "avoid_heavy_load"
This step sends the current system state and operational constraints into the BCADM module.
BCADM evaluates the inputs, applies its multi‑constraint safety logic, and returns a full action‑contract including:

requested vs achieved movement

whether the action was modified

all violated constraints

intervention timestamp

recovery state

final pose

This makes BCADM ideal for safety‑contract validation, constraint‑exercise simulations, and robotics education.