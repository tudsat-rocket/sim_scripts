import math

def shear_tearout_sv(bolts, tube, F_ax):
    # Calculate shear tearout safety factor
    b = tube["bolt_hole_edge_distance"]
    n = bolts["count"]
    s = tube["wall_strength"]
    tau = tube["ultimate_shear_strength"]

    s_v = (2 * b * n * s * tau) / F_ax
    return s_v

def bearing_failure_sv(bolts, tube, F_ax):
    # Calculate bearing failure safety factor
    R_p = tube["yield_strength"]
    n = bolts["count"]
    if bolts["shoulder_used"]:
        d = bolts["shoulder_diameter"]
    else: d = bolts["diameter"]
    s = tube["wall_strength"]

    s_v = (R_p * n * d * s) / F_ax
    return s_v

def net_section_sv(bolts, tube, F_ax):
    # Calculate net section safety factor
    R_m = tube["ultimate_strength"]
    D = tube["outer_diameter"]
    s = tube["wall_strength"]
    d_m = D - s  # middle diameter of tube
    n = bolts["count"]
    if bolts["shoulder_used"]:
        d = bolts["shoulder_diameter"]
    else: d = bolts["diameter"]

    A = (math.pi * d_m * s) - (n * d * s)
    s_v = (R_m * A) / F_ax
    return s_v

def burst_sv(tube, p):
    R_p = tube["yield_strength"]
    s = tube["wall_strength"]
    D = tube["outer_diameter"]

    s_v = (2 * s * R_p) / (p * D)
    return s_v

def burst_p(tube):
    R_p = tube["yield_strength"]
    s = tube["wall_strength"]
    D = tube["outer_diameter"]

    p_burst = (2 * R_p * s) / D
    return p_burst

def s_min(tube, s_v, p):
    R_p = tube["yield_strength"]
    s = tube["wall_strength"]
    D = tube["outer_diameter"]

    s_min = (p * D * s_v) / (2 * R_p)
    return s_min