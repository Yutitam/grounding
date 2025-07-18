import cvxpy as cp
import numpy as np

# Parameters (based on real-world references)
Ig = 63000  # fault current in A
t_fault = 0.7  # seconds
rho_soil = 16.804  # soil resistivity in ohm-m
fixed_len_rod = 5.0  # meters (fixed rod length)
Kr = 1000  # cost of rod per meter (THB)
Kc = 1800  # cost of conductor per meter (THB)
E_step_perm = 1320.08  # permitted step voltage (V)
E_touch_perm = 417.02  # permitted touch voltage (V)

print(f"NOTE: Rod length is fixed at {fixed_len_rod} m.")

# Simplified physical model
def estimate_step_voltage(Ig_val, rho_val, Rg_val):
    return Ig_val * Rg_val * 0.75  # 75% factor for step voltage

def estimate_touch_voltage(Ig_val, rho_val, Rg_val):
    return Ig_val * Rg_val * 0.25  # 25% factor for touch voltage

# Grid resistance estimation (simplified formula)
def calculate_Rg(rho_val, total_rod_length, total_conductor_length):
    effective_area = total_rod_length + 0.5 * total_conductor_length  # rods + contribution from grid
    return rho_val / effective_area

# Optimization variables
num_rods = cp.Variable(pos=True)
len_cond = cp.Variable(pos=True)

# Total lengths
total_rod_length = num_rods * fixed_len_rod
total_conductor_length = len_cond

# Grid resistance expression (as CVXPY expression)
Rg = rho_soil / (total_rod_length + 0.5 * total_conductor_length)

# Estimated voltages (CVXPY expressions)
step_voltage = Ig * Rg * 0.75
touch_voltage = Ig * Rg * 0.25

# Objective function: Minimize cost
cost = total_rod_length * Kr + total_conductor_length * Kc
objective = cp.Minimize(cost)

# Constraints
constraints = [
    step_voltage <= E_step_perm,
    touch_voltage <= E_touch_perm,
    num_rods >= 1,
    len_cond >= 100,
    total_rod_length + total_conductor_length <= 2000  # practical total length limit
]

# Solve problem
problem = cp.Problem(objective, constraints)
problem.solve()

# Results
print("\n--- Optimization Results ---")
if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
    print(f"Problem Status: {problem.status}")
    print(f"Optimal Cost: {problem.value:.2f} THB")
    print(f"Number of Rods: {round(num_rods.value)}")
    print(f"Length of Each Rod (Fixed): {fixed_len_rod:.2f} m")
    print(f"Total Conductor Length: {len_cond.value:.2f} m")
    print(f"Estimated Grid Resistance: {Rg.value:.4f} ohms")
    print(f"Achieved Step Voltage: {step_voltage.value:.2f} V (Permitted: {E_step_perm:.2f} V)")
    print(f"Achieved Touch Voltage: {touch_voltage.value:.2f} V (Permitted: {E_touch_perm:.2f} V)")
else:
    print(f"Problem Status: {problem.status}")
    print("No feasible solution found.")
