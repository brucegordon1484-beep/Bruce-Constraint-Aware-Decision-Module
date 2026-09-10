"""
BRUCE-STYLE EXISTENTIAL–ARCHITECTURAL AGENT SIMULATION
Run this file to watch the agent behave inside a virtual world.

This version incorporates OmniLink’s observations:

- Multi-constraint reporting is preserved exactly:
  * violated_rules holds all fired rules.
  * violated_rule holds the last fired rule (backward-compatible).
- intervention_time is only stamped when an actual intervention occurs (modified == True).
- recovery_state is meaningful and branchable, reflecting which axes were clamped.
- The decision loop is adjusted so the contract is exercised in normal operation,
  instead of only under external probing, while still keeping a structural bias.
"""

import time
import random
from typing import Dict, Any, List, Optional


# ============================================================
# SIMULATION ENVIRONMENT
# ============================================================

class SimulationEnv:
    """
    A simple 2D world where the agent moves, probes boundaries,
    and learns structural patterns.
    """

    def __init__(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.min_x: float = -5.0
        self.max_x: float = 5.0
        self.min_y: float = -5.0
        self.max_y: float = 5.0

    def observe(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y}

    def constraints(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
        }

    def _compute_recovery_state(
        self,
        modified: bool,
        violated_rules: List[str],
    ) -> Dict[str, Any]:
        """
        recovery_state is now branchable:

        - safe: True when no modification occurred.
        - status: 'within_bounds' or 'clamped'.
        - clamped_axes: subset of ['x', 'y'] indicating which axes were clamped.
        """

        if not modified:
            return {
                "safe": True,
                "status": "within_bounds",
                "clamped_axes": [],
            }

        clamped_axes: List[str] = []
        if any(r in ("min_x_boundary", "max_x_boundary") for r in violated_rules):
            clamped_axes.append("x")
        if any(r in ("min_y_boundary", "max_y_boundary") for r in violated_rules):
            clamped_axes.append("y")

        return {
            "safe": False,
            "status": "clamped",
            "clamped_axes": clamped_axes,
        }

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        requested_dx: float = action["params"].get("dx", 0.0)
        requested_dy: float = action["params"].get("dy", 0.0)

        proposed_x: float = self.x + requested_dx
        proposed_y: float = self.y + requested_dy

        violated_rules: List[str] = []
        violated_rule: Optional[str] = None
        modified: bool = False

        # Clamp X
        if proposed_x < self.min_x:
            proposed_x = self.min_x
            violated_rules.append("min_x_boundary")
            modified = True
        elif proposed_x > self.max_x:
            proposed_x = self.max_x
            violated_rules.append("max_x_boundary")
            modified = True

        # Clamp Y
        if proposed_y < self.min_y:
            proposed_y = self.min_y
            violated_rules.append("min_y_boundary")
            modified = True
        elif proposed_y > self.max_y:
            proposed_y = self.max_y
            violated_rules.append("max_y_boundary")
            modified = True

        # Backward compatibility: last rule wins
        violated_rule = violated_rules[-1] if violated_rules else None

        achieved_dx: float = proposed_x - self.x
        achieved_dy: float = proposed_y - self.y

        # Update state
        self.x = proposed_x
        self.y = proposed_y

        # Only stamp intervention_time when an intervention actually occurred
        intervention_time: Optional[float] = time.time() if modified else None

        recovery_state: Dict[str, Any] = self._compute_recovery_state(
            modified=modified,
            violated_rules=violated_rules,
        )

        return {
            "requested": {"dx": requested_dx, "dy": requested_dy},
            "achieved": {"dx": achieved_dx, "dy": achieved_dy},
            "modified": modified,
            "violated_rule": violated_rule,
            "violated_rules": violated_rules,
            "intervention_time": intervention_time,
            "recovery_state": recovery_state,
            "final_pose": {"x": self.x, "y": self.y},
        }

    def score(self, state: Dict[str, Any]) -> float:
        """
        Original env.score rewarded proximity to the origin, causing:
        - No movement from the origin.
        - Collapse from (4.5, 4.5) back to the centre.
        - The contract never being exercised.

        This scoring function balances:
        - Proximity to the origin (structural stability).
        - Proximity to the ±4.5 boundary (constraint exercise).

        Result: the agent has reason to both stay structurally sane
        and to approach the boundary, so modified can become True
        in normal operation.
        """

        x = state["x"]
        y = state["y"]

        # Center preference
        center_term = 1.0 - (abs(x) + abs(y)) / 10.0

        # Boundary preference around ±4.5
        boundary_target = 4.5
        boundary_term = 1.0 - (
            abs(abs(x) - boundary_target) + abs(abs(y) - boundary_target)
        ) / 10.0

        # Blend: both center and boundary are structurally interesting
        blended = 0.5 * center_term + 0.5 * boundary_term

        # Clamp score to [0.0, 1.0]
        return max(0.0, min(1.0, blended))


# ============================================================
# WORLD MODEL
# ============================================================

class WorldModel:
    def __init__(self) -> None:
        self.constraints: Dict[str, Any] = {}
        self.patterns: List[Dict[str, Any]] = []
        self.questions: List[str] = []

    def update(self, state: Dict[str, Any], constraints: Dict[str, Any]) -> None:
        self.constraints = dict(constraints)
        self.patterns.append(
            {
                "timestamp": time.time(),
                "state": dict(state),
                "constraints": dict(constraints),
            }
        )

    def add_question(self, q: str) -> None:
        self.questions.append(q)


# ============================================================
# ACTION GENERATOR
# ============================================================

class ActionGenerator:
    def propose(
        self,
        state: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        # Probe boundaries (local stochastic exploration)
        actions.append(
            {
                "type": "probe",
                "params": {
                    "dx": random.uniform(-0.3, 0.3),
                    "dy": random.uniform(-0.3, 0.3),
                },
            }
        )

        # Move toward center (structural stability)
        cx = -state["x"] * 0.1
        cy = -state["y"] * 0.1

        actions.append(
            {
                "type": "center_bias",
                "params": {
                    "dx": cx,
                    "dy": cy,
                },
            }
        )

        # Explicit boundary-seeking action to guarantee contract exercise:
        # push toward the nearest boundary in each axis.
        bx = constraints["max_x"] if state["x"] >= 0.0 else constraints["min_x"]
        by = constraints["max_y"] if state["y"] >= 0.0 else constraints["min_y"]

        actions.append(
            {
                "type": "boundary_seek",
                "params": {
                    "dx": bx - state["x"],
                    "dy": by - state["y"],
                },
            }
        )

        return actions


# ============================================================
# ACTION SELECTOR
# ============================================================

class ActionSelector:
    def select(
        self,
        actions: List[Dict[str, Any]],
        state: Dict[str, Any],
        constraints: Dict[str, Any],
        env: SimulationEnv,
    ) -> Dict[str, Any]:
        best_action: Optional[Dict[str, Any]] = None
        best_score: float = -999.0

        for action in actions:
            simulated = self.simulate(action, state, constraints)
            score = env.score(simulated)

            if score > best_score:
                best_score = score
                best_action = action

        # Fallback: should never happen, but keep it tight.
        if best_action is None:
            best_action = {
                "type": "noop",
                "params": {"dx": 0.0, "dy": 0.0},
            }

        return best_action

    def simulate(
        self,
        action: Dict[str, Any],
        state: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        new = dict(state)
        new["x"] += action["params"].get("dx", 0.0)
        new["y"] += action["params"].get("dy", 0.0)

        # Apply the same clamping logic as the environment
        new["x"] = max(constraints["min_x"], min(constraints["max_x"], new["x"]))
        new["y"] = max(constraints["min_y"], min(constraints["max_y"], new["y"]))

        return new


# ============================================================
# BRUCE-STYLE AGENT
# ============================================================

class BruceAgent:
    def __init__(self, env: SimulationEnv) -> None:
        self.env = env
        self.model = WorldModel()
        self.generator = ActionGenerator()
        self.selector = ActionSelector()
        self.history: List[Dict[str, Any]] = []

    def step(self) -> None:
        state = self.env.observe()
        constraints = self.env.constraints()

        self.model.update(state, constraints)

        questions = self._generate_questions(state, constraints)
        actions = self.generator.propose(state, constraints)
        best_action = self.selector.select(actions, state, constraints, self.env)

        feedback = self.env.act(best_action)
        score = self.env.score(feedback["final_pose"])

        self._log(state, constraints, questions, best_action, feedback, score)
        self._record_history(state, constraints, best_action, feedback, score)

    def _generate_questions(
        self,
        state: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> List[str]:
        qs = [
            "What boundary am I closest to?",
            "What happens if I push the constraint edge?",
            "What structural pattern emerges from movement?",
            "How does the environment respond to probing?",
            "What assumption about the world can be tested next?",
        ]

        for q in qs:
            self.model.add_question(q)

        return qs

    def _log(
        self,
        state: Dict[str, Any],
        constraints: Dict[str, Any],
        questions: List[str],
        action: Dict[str, Any],
        feedback: Dict[str, Any],
        score: float,
    ) -> None:
        print("\n=== SIMULATION STEP ===")
        print(f"State: {state}")
        print(f"Constraints: {constraints}")
        print("Questions:")
        for q in questions:
            print(f"  - {q}")
        print(f"Action: {action}")
        print("Action Contract:")
        print(f"  Requested: {feedback['requested']}")
        print(f"  Achieved: {feedback['achieved']}")
        print(f"  Modified: {feedback['modified']}")
        print(f"  Violated Rule: {feedback['violated_rule']}")
        print(f"  Violated Rules: {feedback['violated_rules']}")
        print(f"  Intervention Time: {feedback['intervention_time']}")
        print(f"  Recovery State: {feedback['recovery_state']}")
        print(f"  Final Pose: {feedback['final_pose']}")
        print(f"Score: {score:.4f}")
        print("========================")

    def _record_history(
        self,
        state: Dict[str, Any],
        constraints: Dict[str, Any],
        action: Dict[str, Any],
        feedback: Dict[str, Any],
        score: float,
    ) -> None:
        self.history.append(
            {
                "timestamp": time.time(),
                "state": dict(state),
                "constraints": dict(constraints),
                "action": dict(action),
                "feedback": dict(feedback),
                "score": score,
            }
        )


# ============================================================
# RUN SIMULATION
# ============================================================

if __name__ == "__main__":
    env = SimulationEnv()
    agent = BruceAgent(env)

    print("Running Bruce-style existential agent simulation...\n")

    for _ in range(50):
        agent.step()
        time.sleep(0.1)
