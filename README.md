# Bruce‑Constraint‑Aware‑Decision‑Module (BCADM)

## Action‑Contract System (v1.1 Update)

The BCADM now includes a full safety‑aware action‑contract returned by the environment whenever an agent issues a movement command. This replaces the previous behavior where only the final pose was returned.

This update makes constraint interventions explicit and prevents upstream agents from mistaking a clamped or safety‑modified action for a fully executed one. It also makes the module suitable for multi‑agent systems, planners, supervisors, and democratized robotics environments.

## What the environment returns now

Each call to `env.act()` returns a structured contract:

- **requested** – the movement the agent attempted  
- **achieved** – the movement actually executed after clamping  
- **modified** – whether the action was changed for safety  
- **violated_rule** – the last boundary constraint that fired (legacy compatibility)  
- **violated_rules** – *all* constraints that fired (new in v1.1)  
- **intervention_time** – timestamp of the safety intervention  
- **recovery_state** – environment’s safety status  
- **final_pose** – the resulting position after movement  

BCADM v1.1 resolves the previous observability gap where simultaneous X/Y boundary violations would overwrite each other. The module now provides complete multi‑constraint visibility for robotics workflows, planners, and agent‑based systems.
