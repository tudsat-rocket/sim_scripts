import math

import libs.tube_calc as tube_calc

###
#Cilindrical Pressure Container Calculator
#   Calculates the safety, theoretical maximum pressure and minimum wall strength of a homogenous tube against bursting and prints them into console.
#   Barlow's formula is used for this (DIN 2413).
###

## Set values for the calculation here:
#   Tube:
tube = {
    "outer_diameter": 150e-3,  # [m]
    "wall_strength": 5e-3,     # [m]
    "length": 630e-3,          # [m]
    "ultimate_strength": 350e6,   # "Festigkeit" [Pa]
    "yield_strength": 255e6,    # "Streckgrenze" [Pa]
}

## Load Case:
p = 5.5e6  # inner pressure [Pa]
S_v = 2.5  # goal safety factor

## Calculation & Output
print("\n")
print(f"The calculated safety factor against burst is: {tube_calc.burst_sv(tube, p)}  ,")
print(f"with a theoretical burst pressure of {tube_calc.burst_p(tube) / 1e6}MPa or {tube_calc.burst_p(tube) / 1e5}bar")
print(f"and a minimum wall strength of {tube_calc.s_min(tube, S_v, p) * 1e3}mm.")
print("")