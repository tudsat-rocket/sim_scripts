import rocketpy

import datetime
import math

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path

import libs.data_handler as data_handler

#IMPORTANT
# rocketpy and yaml libraries are needed to run this
# please install them using
# 'pip install rocketpy'
# 'pip install pyyaml'

#FILES
drag_pwr_off = Path(__file__).parent / "data/drag/DragPwrOff.csv"
drag_pwr_on = Path(__file__).parent / "data/drag/DragPwrOn.csv"
fin_lift = Path(__file__).parent / "data/lift/naca_0008_final.csv"
engine_thrust = Path(__file__).parent / "data/thrust/hyacinth_engine.csv"

valis = data_handler.load_data(Path(__file__).parent / "data/valispace/vali_sim_data.yaml")

#EuRoC launch site
launch_environment = rocketpy.Environment(
    latitude = valis["LaunchEnvironment"]["latitude"],
    longitude = valis["LaunchEnvironment"]["longitude"],
    elevation = valis["LaunchEnvironment"]["elevation"]
)

#time within competition time frame (09/10-15/10, launches likely 10/10-14/10)
launch_environment.set_date(
    (2025, 10, 12, 12), timezone="Europe/Lisbon"
)

#mostly ISA
launch_environment.set_atmospheric_model(
    type="custom_atmosphere",
    pressure=None,
    temperature=None,
    #Wind Scenarios based on historical data

    #Scenario 1: 330° 4 m/s - 10 m/s
    #wind_u = [(0, -2.00),(3000, -5.00)],
    #wind_v = [(0, 3.46),(3000, 8.66)],
    
    #Scenario 2: 330° 7 m/s - 20 m/s
    #wind_u = [(0, -3.50),(3000, -10.00)],
    #wind_v = [(0, 6.06),(3000, 17.32)],
    
    #Scneario 3: 210° 4 m/s - 10 m/s
    wind_u = [(0, -2.00),(3000, -5.00)],
    wind_v = [(0, -3.46),(3000, -8.66)],
    
    #Secnario 4: 210° 7 m/s - 20 m/s
    #wind_u = [(0, -3.50),(3000, -10.00)],
    #wind_v = [(0, -6.06),(3000, -17.32)],
)
#TANKS
#set properties of Nitrous Oxide
liquid_N2O = rocketpy.Fluid(name="Liquid Nitrous Oxide", density = valis["NitrousOxide"]["density"])

#properties of Nitrogen
vapour_N = rocketpy.Fluid(name="Gaseous Nitrogen", density=1200)

#set oxidizer tank geometry
ox_tank_geometry = rocketpy.CylindricalTank(
    radius = valis["OxidizerTank"]["inner_diameter"]/2,
    height = valis["OxidizerTank"]["inner_height"],
    spherical_caps=False
)


time_burn = valis["C_Propulsion_Module"]["time_burn"]
mass_ox = valis["NitrousOxide"]["mass_oxidizer"]

#oxidizer tank
oxidizer_tank = rocketpy.MassFlowRateBasedTank(
    name = "Oxidizer_Tank",
    geometry = ox_tank_geometry,
    flux_time = time_burn,
    gas = vapour_N, #doesn't do anything, just needs to exist
    liquid = liquid_N2O,
    initial_gas_mass = 0,
    initial_liquid_mass = mass_ox,
    liquid_mass_flow_rate_in = 0,
    #liquid_mass_flow_rate_out = valis["NitrousOxide"]["mass_oxidizer"]/valis["C_Propulsion_Module"]["time_burn"],
    liquid_mass_flow_rate_out = lambda t: min(t * mass_ox*5/(time_burn**2), mass_ox/time_burn*10/math.sqrt(90)) if t<(time_burn/2) else min(mass_ox/time_burn*20 - t * mass_ox*5/(time_burn**2), mass_ox/time_burn * 10 / math.sqrt(90)),
    gas_mass_flow_rate_in = valis["Nitrogen"]["mass_pressurant"]/valis["C_Propulsion_Module"]["time_burn"],
    gas_mass_flow_rate_out = 0,
    discretize=100
)

#set pressurant tank geometry
press_tank_geometry = rocketpy.CylindricalTank(
    radius = valis["PressurantTank"]["inner_diameter"]/2,
    height = valis["PressurantTank"]["inner_height"],
    spherical_caps = True
)

#pressurant tank
pressurant_tank = rocketpy.MassFlowRateBasedTank(
    name = "Pressurant_Tank",
    geometry = press_tank_geometry,
    flux_time = valis["C_Propulsion_Module"]["time_burn"],
    gas = vapour_N,
    liquid = liquid_N2O, #doesn't do anything, just needs to exist
    initial_gas_mass = valis["Nitrogen"]["mass_pressurant"]+1e-10,
    initial_liquid_mass = 0,
    liquid_mass_flow_rate_in = 0,
    liquid_mass_flow_rate_out = 0,
    gas_mass_flow_rate_in = 0,
    #gas_mass_flow_rate_out =
    gas_mass_flow_rate_out = valis["Nitrogen"]["mass_pressurant"]/valis["C_Propulsion_Module"]["time_burn"],
    discretize=100
)

#MOTOR
#coordinate system for motor and tanks is inverted to normal coordinate system and relative to the nozzle exit plane
hyacinth_motor = rocketpy.HybridMotor(
    thrust_source=engine_thrust,
    interpolation_method="spline",
    #thrust_source=lambda t: valis["C_Propulsion_Module"]["thrust"]-t*120,#2500N@0s -> 1900N@5s
    dry_mass=0,
    dry_inertia=(0, 0, 0),
    nozzle_radius=valis["Nozzle"]["exit_diameter"]/2,
    grain_number=1,
    grain_separation=0,
    grain_outer_radius=valis["SolidFuel"]["outer_diameter"]/2,
    grain_initial_inner_radius=valis["SolidFuel"]["inner_diameter"]/2,
    grain_initial_height=valis["SolidFuel"]["length"],
    grain_density=valis["SolidFuel"]["density"],
    grains_center_of_mass_position=valis["Rocket"]["length"]-valis["SolidFuel"]["CoM"],
    center_of_dry_mass_position=0,
    nozzle_position=0,
    burn_time=valis["C_Propulsion_Module"]["time_burn"],
    throat_radius=valis["Nozzle"]["throat_diameter"]/2,
)

hyacinth_motor.add_tank(
    tank=oxidizer_tank,
    position=valis["Rocket"]["length"]-valis["OxidizerTank"]["CoM"],
)

hyacinth_motor.add_tank(
    tank=pressurant_tank,
    position=valis["Rocket"]["length"]-valis["PressurantTank"]["CoM"]
)

#definition of values for inertia calculation
height = valis["Rocket"]["length"]
mass = valis["Rocket"]["mass"]
radius = valis["Rocket"]["radius"]

#inertia calculation based on ideal cylinders
com = data_handler.center_of_mass(valis)
inertia_axial, inertia_radial = data_handler.inertia(valis, com, radius)

#ROCKET
hyacinth = rocketpy.Rocket(
    radius=radius,
    mass=mass,
    inertia=(inertia_radial, inertia_radial, inertia_axial),
    power_off_drag = drag_pwr_off,
    power_on_drag = drag_pwr_on,
    center_of_mass_without_motor=com, #coordinate system same as OpenRocket and RasAero
    coordinate_system_orientation="nose_to_tail"
)

buttons = hyacinth.set_rail_buttons(
    upper_button_position=valis["RailButtonFront"]["CoM"],
    lower_button_position=valis["RailButtonRear"]["CoM"],
)

hyacinth.add_motor(hyacinth_motor, position=height)

#add von karman nose cone
hyacinth.add_nose(
    length=valis["NoseCone"]["conical_length"],
    kind="von karman",
    position=0,
)

#add fin set
hyacinth.add_trapezoidal_fins(
    n=3,
    root_chord=valis["FinCan"]["fins_root_chord"],
    tip_chord=valis["FinCan"]["fins_tip_chord"],
    span=valis["FinCan"]["fins_span"],
    position=height-valis["FinCan"]["fins_root_chord"],
    sweep_length=valis["FinCan"]["fins_sweep_length"],
    airfoil=(fin_lift,"degrees")
)

#add boattail
hyacinth.add_tail(
    top_radius=radius,
    bottom_radius=valis["FinCan"]["boattail_bottom_radius"],
    length=valis["FinCan"]["boattail_length"],
    position=height-valis["FinCan"]["boattail_length"]
)

#CHUTES

#Second Event
#area contains all parachutes, i.e. main, pilot and parabrakes
hyacinth.add_parachute(
    name="main",
    cd_s=2.2*math.pi*(1.8288/2)**2 + 1.5*math.pi*(0.4572/2)**2 + 0.351,
    trigger=450,
    sampling_rate=100,
    lag=1.5,
    noise=(0,0,0)
)

#First Event (Parabrakes)
hyacinth.add_parachute(
    name="parabrakes",
    cd_s = 0.351,
    trigger="apogee",
    sampling_rate=100,
    lag = 3,
    noise = (0,0,0)
)

#LAUNCH
euroc2025 = rocketpy.Flight(
    environment=launch_environment,
    rocket=hyacinth,
    rail_length=valis["LaunchEnvironment"]["rail_length"],
    inclination=valis["LaunchEnvironment"]["inclination"],
    heading=valis["LaunchEnvironment"]["heading"],
)


#PRINTS AND PLOTS

#printing values
if False:
    euroc2025.prints.maximum_values()

    euroc2025.prints.out_of_rail_conditions()

    euroc2025.prints.apogee_conditions()

    euroc2025.prints.impact_conditions()

    euroc2025.prints.events_registered()

    hyacinth.prints.inertia_details()

    hyacinth_motor.all_info()

#plotting values
if False:
    hyacinth.plots.static_margin()

    euroc2025.plots.stability_and_control_data()

    hyacinth.draw()

    euroc2025.plots.trajectory_3d()

    euroc2025.plots.linear_kinematics_data()

    hyacinth.plots.total_mass()


def stability_plot():
    plt.figure(figsize=(7, 4))

    ax1 = plt.subplot()
    ax1.plot(euroc2025.stability_margin[:, 0], euroc2025.stability_margin[:, 1])
    #ax1.set_xlim(0, euroc2025.stability_margin[:, 0][-1])
    ax1.set_title("Stability Margin")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Stability Margin (c)")
    ax1.set_xlim(0, euroc2025.parachute_events[0][0]+1)
    ax1.axvline(
        x=euroc2025.out_of_rail_time,
        color="r",
        linestyle="--",
        label="Out of Rail Time",
    )
    ax1.axvline(
        x=euroc2025.rocket.motor.burn_out_time,
        color="g",
        linestyle="--",
        label="Burn Out Time",
    )

    ax1.axvline(
        x=euroc2025.apogee_time,
        color="m",
        linestyle="--",
        label="Apogee Time",
    )
    ax1.legend()
    ax1.grid()
    rocketpy.plots.plot_helpers.show_or_save_plot("stability.png")




def velocity_plot():
    plt.figure(figsize=(7, 4))

    ax1 = plt.subplot()
    ax1.plot(euroc2025.speed[:, 0], euroc2025.speed[:, 1])
    #ax1.set_xlim(0, euroc2025.stability_margin[:, 0][-1])
    ax1.set_title("Velocity")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Velocity (m/s)")
    ax1.set_xlim(0, euroc2025.t_final)
    ax1.axvline(
        x=euroc2025.out_of_rail_time,
        color="r",
        linestyle="--",
        label="Out of Rail Time",
    )
    ax1.axvline(
        x=euroc2025.rocket.motor.burn_out_time,
        color="g",
        linestyle="--",
        label="Burn Out Time",
    )

    ax1.axvline(
        x=euroc2025.apogee_time,
        color="m",
        linestyle="--",
        label="Apogee Time",
    )
    ax1.axvline(
        x=euroc2025.parachute_events[1][0],
        color="gold",
        linestyle="--",
        label="Main Parachute Deploy",
    )

    ax1.legend()
    ax1.grid()
    rocketpy.plots.plot_helpers.show_or_save_plot("velocity.png")


def acceleration_plot():
    plt.figure(figsize=(7, 4))

    ax1 = plt.subplot()
    ax1.plot(euroc2025.acceleration[:, 0], euroc2025.acceleration[:, 1])
    #ax1.set_xlim(0, euroc2025.stability_margin[:, 0][-1])
    ax1.set_title("Acceleration")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Acceleration (m/s²)")
    ax1.set_xlim(0, euroc2025.t_final)
    ax1.axvline(
        x=euroc2025.out_of_rail_time,
        color="r",
        linestyle="--",
        label="Out of Rail Time",
    )
    ax1.axvline(
        x=euroc2025.rocket.motor.burn_out_time,
        color="g",
        linestyle="--",
        label="Burn Out Time",
    )

    ax1.axvline(
        x=euroc2025.apogee_time,
        color="m",
        linestyle="--",
        label="Apogee Time",
    )
    ax1.axvline(
        x=euroc2025.parachute_events[1][0],
        color="gold",
        linestyle="--",
        label="Main Parachute Deploy",
    )

    ax1.legend()
    ax1.grid()
    rocketpy.plots.plot_helpers.show_or_save_plot("acceleration.png")


def com_cop_plot():
    plt.figure(figsize=(7, 4))

    ax1 = plt.subplot()
    x_axis= np.arange(0, euroc2025.parachute_events[0][0]+1, 0.1)
    ax1.plot(x_axis, hyacinth.center_of_mass(x_axis), label = "COM")
    ax1.plot(x_axis, hyacinth.cp_position(euroc2025.mach_number(x_axis)), label = "COP")
    #ax1.set_xlim(0, euroc2025.stability_margin[:, 0][-1])
    ax1.set_title("COM / COP")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("COM position / COP position (m)")
    ax1.set_xlim(0, euroc2025.parachute_events[0][0]+1)
    ax1.axvline(
        x=euroc2025.out_of_rail_time,
        color="r",
        linestyle="--",
        label="Out of Rail Time",
    )
    ax1.axvline(
        x=euroc2025.rocket.motor.burn_out_time,
        color="g",
        linestyle="--",
        label="Burn Out Time",
    )

    ax1.axvline(
        x=euroc2025.apogee_time,
        color="m",
        linestyle="--",
        label="Apogee Time",
    )

    ax1.legend()
    ax1.grid()
    rocketpy.plots.plot_helpers.show_or_save_plot("com_cop.png")

#Plots for Technical Report
#!!!These save images as files

if False:
    stability_plot()
    velocity_plot()
    acceleration_plot()
    com_cop_plot()

#Prints for Technical Report

if False:
    print(f"Expected Point of Descend: {math.sqrt((euroc2025.x(0)-euroc2025.x_impact)**2 + (euroc2025.y(0)-euroc2025.y_impact)**2)} m")

    euroc2025.prints.events_registered()
    euroc2025.prints.apogee_conditions()
    euroc2025.prints.impact_conditions()

    euroc2025.plots.trajectory_3d(filename="3d_trajectory.png")

    print(euroc2025.speed(euroc2025.parachute_events[0][0]+10))


