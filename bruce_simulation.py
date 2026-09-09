"""
BRUCE-STYLE EXISTENTIAL–ARCHITECTURAL AGENT SIMULATION
Run this file to watch the agent behave inside a virtual world.
"""

import time
import random
from typing import Dict, Any, List


# ============================================================
# SIMULATION ENVIRONMENT
# ============================================================

class SimulationEnv:
    """
    A simple 2D world where the agent moves, probes boundaries,
    and learns structural patterns.
    """

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.min_x = -5.0
        self.max_x = 5.0
        self.min_y = -5.0
        self.max_y = 5.0

    def observe(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y}

    def constraints(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
        }

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        requested_dx = action["params"].get("dx", 0.0)
        requested_dy = action["params"].get("dy", 0.0)

        proposed_x = self.x + requested_dx
        proposed_y = self.y + requested_dy

        violated_rules = []
        violated_rule = None
        modified = False

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

        achieved_dx = proposed_x - self.x
        achieved_dy = proposed_y - self.y

        # Update state
        self.x = proposed_x
        self.y = proposed_y

        return {
            "requested": {"dx": requested_dx, "dy": requested_dy},
            "achieved": {"dx": achieved_dx, "dy": achieved_dy},
            "modified": modified,
            "violated_rule": violated_rule,
            "violated_rules": violated_rules,
            "intervention_time": time.time(),
            "recovery_state": {"safe": True},
            "final_pose": {"x": self.x, "y": self.y}
        }

    def score(self, state: Dict[str, Any]) -> float:
        return 1.0 - (abs(state["x"]) + abs(state["y"])) / 10.0


# ============================================================
# WORLD MODEL
# ============================================================

class WorldModel:
    def __init__(self):
        self.constraints = {}
        self.patterns = []
        self.questions = []

    def update(self, state, constraints):
        self.constraints = constraints
        self.patterns.append({
            "timestamp": time.time(),
            "state": state,
            "constraints": constraints,
        })

    def add_question(self, q):
        self.questions.append(q)


# ============================================================
# ACTION GENERATOR
# ============================================================

class ActionGenerator:
    def propose(self, state, constraints):
        actions = []

        # Probe boundaries
        actions.append({
            "type": "probe",
            "params": {
                "dx": random.uniform(-0.3, 0.3),
                "dy": random.uniform(-0.3, 0.3),
            }
        })

        # Move toward center
        cx = -state["x"] * 0.1
        cy = -state["y"] * 0.1

        actions.append({
            "type": "center_bias",
            "params": {
                "dx": cx,
                "dy": cy,
            }
        })

        return actions


# ============================================================
# ACTION SELECTOR
# ============================================================

class ActionSelector:
    def select(self, actions, state, constraints, env):
        best_action = None
        best_score = -999

        for action in actions:
            simulated = self.simulate(action, state, constraints)
            score = env.score(simulated)

            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def simulate(self, action, state, constraints):
        new = dict(state)
        new["x"] += action["params"].get("dx", 0.0)
        new["y"] += action["params"].get("dy", 0.0)

        new["x"] = max(constraints["min_x"], min(constraints["max_x"], new["x"]))
        new["y"] = max(constraints["min_y"], min(constraints["max_y"], new["y"]))

        return new


# ============================================================
# BRUCE-STYLE AGENT
# ============================================================

class BruceAgent:
    def __init__(self, env):
        self.env = env
        self.model = WorldModel()
        self.generator = ActionGenerator()
        self.selector = ActionSelector()
        self.history = []

    def step(self):
        state = self.env.observe()
        constraints = self.env.constraints()

        self.model.update(state, constraints)

        questions = self._generate_questions(state, constraints)
        actions = self.generator.propose(state, constraints)
        best_action = self.selector.select(actions, state, constraints, self.env)

        feedback = self.env.act(best_action)
        score = self.env.score(feedback["final_pose"])

        self._log(state, constraints, questions, best_action, feedback, score)

    def _generate_questions(self, state, constraints):
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

    def _log(self, state, constraints, questions, action, feedback, score):
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
        print(f"  Final Pose: {feedback['final_pose']}")
        print(f"Score: {score}")
        print("========================")


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
