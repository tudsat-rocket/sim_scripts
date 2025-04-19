import math

def fastener_shear_sv(bolts, F_shear):
    # Calculate fastener shear safety factor
    n = bolts["count"]
    if bolts["shoulder_used"]:
        d = bolts["shoulder_diameter"]
    else:
        d = bolts["thread_inner_diameter"]
    A = math.pi*(d/2)**2
    tau = bolts["tau_rho"]

    s_v = (n * A * tau) / F_shear
    return s_v
    