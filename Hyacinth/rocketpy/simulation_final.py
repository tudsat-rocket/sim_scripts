import rocketpy

import datetime
import math

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
    wind_u = 0,
    wind_v = -3,
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

#oxidizer tank
oxidizer_tank = rocketpy.MassFlowRateBasedTank(
    name = "Oxidizer_Tank",
    geometry = ox_tank_geometry,
    flux_time = valis["C_Propulsion_Module"]["time_burn"],
    gas = vapour_N, #doesn't do anything, just needs to exist
    liquid = liquid_N2O,
    initial_gas_mass = 0,
    initial_liquid_mass = valis["NitrousOxide"]["mass_oxidizer"],
    liquid_mass_flow_rate_in = 0,
    liquid_mass_flow_rate_out = valis["NitrousOxide"]["mass_oxidizer"]/valis["C_Propulsion_Module"]["time_burn"],
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
    gas_mass_flow_rate_out = valis["Nitrogen"]["mass_pressurant"]/valis["C_Propulsion_Module"]["time_burn"],
    discretize=100
)

#MOTOR
#coordinate system for motor and tanks is inverted to normal coordinate system and relative to the nozzle exit plane
hyacinth_motor = rocketpy.HybridMotor(
    thrust_source=lambda t: valis["C_Propulsion_Module"]["thrust"]-t*120,#2500N@0s -> 1900N@5s
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
    cd_s=2.2*math.pi*(1.8288/2)**2 + 1.5*math.pi*(0.4572/2)**2 + 1.2 * math.pi * (0.35**2 - 0.075**2),
    trigger=450,
    sampling_rate=100,
    lag=1.5,
    noise=(0,0,0)
)

#First Event (Parabrakes)
hyacinth.add_parachute(
    name="parabrakes",
    cd_s = 1.2 * math.pi * (0.35**2 - 0.075**2),
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
if True:
    euroc2025.prints.maximum_values()

    euroc2025.prints.out_of_rail_conditions()

    euroc2025.prints.apogee_conditions()

    euroc2025.prints.impact_conditions()

    euroc2025.prints.events_registered()

    hyacinth.prints.inertia_details()

#plotting values
if True:
    hyacinth.plots.static_margin()

    hyacinth.draw()

    euroc2025.plots.trajectory_3d()

    euroc2025.plots.linear_kinematics_data()

    hyacinth.plots.total_mass()
