"""
Implementation of equations found in "E. Messerschmid, S. Fasoulas: Raumfahrtsysteme,
Springer-Verlag, Berlin (2017)".

Original Author Jesko F., edited by Manuel B. 
Disclaimer: not everything running, just the nozzle calculation.

"""
#import numpy as np
import math as np  #sry
#import scipy.constants as const


# Input Parameters
pressure_inlet = 26 * 1e5
pressure_exit = 1 * 1e5
pressure_ambient = 1 * 1e5
temperature_inlet = 3000
heat_capacity_ratio = 1.25
mass_flow = 1.3
molar_mass = 29 * 1e-3

def get_force(self, p0, t0, pa):
    mass_flow = TAU * p0 * self.area_throat
    pressure_exit = 0
    velocity_exit = np.sqrt((2*K)/(K-1) * const.R/MOLAR_MASS * t0 * (1 - np.power(pressure_exit/p0, (K-1)/K)))

    force = mass_flow * velocity_exit + self.area_exit * (pressure_exit - pa)
    return force

def get_area_throat(p0, t0, k, dm, mm):
    """
    Calculates the throat area required for transsonic flow at the throat. Calculations
    are performed in SI units and are based on equations 5.47, 5.48 in [1].
    params:
        p0: pressure at the inlet
        t0: temperature at the inlet
        k: heat capacity ratio
        dm: mass flow
        mm: molar mass
    returns:
        area_throat: throat area
    """
    tau = np.sqrt(k * np.pow(2/(k+1), (k+1)/(k-1)))
    area_throat = dm * np.sqrt(8.3145/mm * t0) / (p0 * tau)

    return area_throat

def get_mach_number(p, p0, k):
    """
    Calculates the mach number on a flow line from inlet to exit. Calculations
    are performed in SI units and are based on equation 5.33 in [1].
    params:
        p: pressure at the point of interest
        p0: pressure at the inlet
        t0: temperature at the inlet
        k: heat capacity ratio
        mm: molar mass
    returns:
        mach_number: mach number at the point of interest
    """
    mach_number = np.sqrt(2/(k-1) * (np.pow(p0/p, (k-1)/k) - 1))

    return mach_number

def get_velocity(p, p0, t0, k, mm):
    """
    Calculates the flow velocity on a flow line from inlet to exit. Calculations
    are performed in SI units and are based on equations 5.30, 5.31, 5.35 in [1].
    Valid for frictionless flow without external exchange of heat in 1D.
    params:
        p: pressure at the point of interest
        p0: pressure at the inlet
        t0: temperature at the inlet
        k: heat capacity ratio
        mm: molar mass
    returns:
        velocity: mach number at the point of interest
    """
    velocity = np.sqrt((2*k)/(k-1) * 8.3145/mm * t0 * (1 - np.pow(p/p0, (k-1)/k)))

    return velocity

def get_expansion_ratio_local(ma, k):
    """
    Calculates the nozzle area relative to the throat area. Calculations
    are performed in SI units and are based on equation 5.42 in [1].
    params:
        ma: mach number at the point of interest
        k: heat capacity ratio
    returns:
        expansion_ratio_local: expansion ratio at the point of interest
    """
    expansion_ratio_local = 1/ma * np.pow(2/(k+1) * (1 + (k-1)/2 * ma*ma), (k+1)/(2*(k-1)))

    return expansion_ratio_local

def get_force(ve, dm, pe, pa, ae):
    """
    Calculates the thrust force. Calculations are performed in
    SI units and are based on equation 5.42 in [1].
    params:
        ve: exit velocity
        dm: mass flow
        pe: pressure at the exit
        pa: ambient pressure
        ae: exit area
    returns:
        force: thrust force
    """
    force = dm * ve + ae * (pe - pa)

    return force

def get_isp(f, dm):
    """
    Calculates the specific impulse. Calculations are performed in
    SI units and are based on equation 5.42 in [1].
    params:
        f: force
        dm: mass flow
    returns:
        isp: specific impulse
    """
    isp = f / (9.81 * dm)

    return isp

def print_inputs():
    # printout Inputs
    print()
    print("Input Parameters:")
    print("pressure_inlet [Pa]: ", pressure_inlet)
    print("pressure_exit [Pa]: ", pressure_exit)
    print("pressure_ambient [Pa]: ", pressure_ambient)
    print("temperature_inlet [K]: ", temperature_inlet)
    print("heat_capacity_ratio: ", heat_capacity_ratio)
    print("mass_flow [kg/s]: ", mass_flow)
    print("molar_mass [kg/mol]: ", molar_mass)
    print()

def calc_and_print_results():
    # printout Results
    print("Results:")
    area_throat = get_area_throat(pressure_inlet, temperature_inlet, heat_capacity_ratio, mass_flow, molar_mass)
    radius_throat = np.sqrt(area_throat / np.pi)
    print("radius throat [mm]:", radius_throat * 1e3)

    mach_number_exit = get_mach_number(pressure_exit, pressure_inlet, heat_capacity_ratio)
    print("mach number exit:", mach_number_exit)

    velocity_exit = get_velocity(pressure_exit, pressure_inlet, temperature_inlet, heat_capacity_ratio, molar_mass)
    print("velocity exit [m/s]:", velocity_exit)

    expansion_ratio = get_expansion_ratio_local(mach_number_exit, heat_capacity_ratio)
    print("expansion ratio:", expansion_ratio)
    area_exit = area_throat * expansion_ratio
    radius_exit = np.sqrt(area_exit / np.pi)
    print("radius exit [mm]:", radius_exit * 1e3)

    force = get_force(velocity_exit, mass_flow, pressure_exit, pressure_ambient, area_exit)
    print("thrust [N]:", force)

    isp = get_isp(force, mass_flow)
    print("Isp [s]:", isp)

    print()


# run
print_inputs()
calc_and_print_results()
