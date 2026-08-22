# Bruce-Constraint-Aware-Decision-Module
BSDE provides a stability-first control loop that:  identifies constraints  avoids unsafe boundaries  maintains equilibrium  probes gently  adapts each step  produces interpretable reasoning logs  Perfect for:  humanoid robot decision layers  safe-mode controllers  mobile robot navigation  drone stability logic  research experiments  ROS2 
- name: BSDE Decision
  uses: Bruce/BSDE@v1
  with:
    state: "battery_low"
    constraints: "avoid_heavy_load"
