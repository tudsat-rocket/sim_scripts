import math

import libs.bolt_calc as bolt_calc
import libs.tube_calc as tube_calc

###
# Radial Bolt Tube Connection Calculator
#   Calculates the safeties of a radial tube bolt connection against 4 common failure modes, using approximating formulas for bolt - sheet metal connections 
#   and prints them into console.
#   The tested failure modes are
#       Shearing of fastener
#       Shear tearout from tube
#       Bearing failure of bolt hole in tube
#       Net Section failure of remaining tube cross section
###

## Set values for the calculation here:
#   Tube:
tube = {
    "outer_diameter": 108e-3,  # [m]
    "wall_strength": 4e-3,     # [m]
    "length": 630e-3,          # [m]
    "ultimate_strength": 255e6,   # "Festigkeit" [Pa]
    "yield_strength": 160e6,    # "Streckgrenze" [Pa]
    "ultimate_shear_strength": 150e6,  # "Scherfestigkeit" [Pa]
    "bolt_hole_edge_distance": 10e-3   # distance from edge to hole center [m]
}

#   Bolts:
bolts = {
    "count": 7,               # []
    "diameter": 10e-3,          # [m]
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
F_ax = 19900 # axial Load [N]


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