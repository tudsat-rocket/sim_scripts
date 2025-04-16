import math

import libs.bolt_calc as bolt_calc
import libs.tube_calc as tube_calc


## Set values for the calculation here:
#   Tube:
tube = {
    "outer_diameter": 150e-3,  # [m]
    "wall_strength": 5e-3,     # [m]
    "length": 630e-3,          # [m]
    "ultimate_strength": 350e6,   # "Festigkeit" [Pa]
    "yield_strength": 255e6,    # "Streckgrenze" [Pa]
    "ultimate_shear_strength": 210e6,  # "Scherfestigkeit" [Pa]
    "bolt_hole_edge_distance": 15e-3   # distance from edge to hole center [m]
}

#   Bolts:
bolts = {
    "count": 10,               # []
    "diameter": 8e-3,          # [m]
    "thread_inner_diameter": 6.78e-3, # [m]
    "shoulder_diameter": 10e-3, # [m]
    "total_length": 30e-3,     # [m]
    "thread_length": 18e-3,    # [m]
    "shoulder_used": True,     # set this if the force is transferred through the shoulder
    "strength_class": 12.9     # acc to DIN 898-1[]
}

#   Global Safety Goal
S_v = 4  #specify required safety value here

#   Load Case
F_ax = 89573 # axial Load [N]


## Precalculations, do not change

if bolts["strength_class"] != 0 and type(bolts["strength_class"]) == float:  # if regular strength class is given
    b_re_v, b_rm = math.modf(bolts["strength_class"]) 
    bolts["ultimate strength"] = b_rm * 1e8  #"Festigkeit" [Pa]
    bolts["yield_strength"] = bolts["ultimate strength"] * b_re_v  #"Streckgrenze" [Pa]

tau_rho = { # shear strengths acc to DIN 898-1
    4.6 : 280e6,
    5.6 : 350e6,
    8.8 : 520e6,
    10.9 : 620e6,
    12.9 : 720e6
}

bolts["tau_rho"] = tau_rho[bolts["strength_class"]]


## Calculation & Output
print("\n")
print("The calculated safeties are as following:")
print("")
print(f"Fastener Shear Safety: {bolt_calc.fastener_shear_sv(bolts, F_ax)}")
print(f"Shear Tearout Safety: {tube_calc.shear_tearout_sv(bolts, tube, F_ax)}")
print(f"Bearing Failure of Tube Safety: {tube_calc.bearing_failure_sv(bolts, tube, F_ax)}")
print(f"Net Section Safety: {tube_calc.net_section_sv(bolts, tube, F_ax)}")
print("")