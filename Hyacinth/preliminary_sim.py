import rocketpy

import datetime
import math

#set environment to actual launch site
launch_environment = rocketpy.Environment(
    latitude = 39.39011270334382,
    longitude = -8.28928771347388,
)

#set time to within competition time frame
#TODO more accurate
launch_environment.set_date(
    (2025, 10, 12, 12), timezone="Europe/Lisbon"
)

#sample wind and temperature based on historical data
launch_environment.set_atmospheric_model(
    type="custom_atmosphere",
    pressure=None,
    temperature=None,
    #TODO change this to historical wind
    #TODO potenital pressure and temperature with custom atmosphere
    wind_u = [(0,-1.5), (1000, -5)],
    wind_v = [(0,-0.5), (1000, -2)],
)

#use OpenElevation for elevation data
launch_environment.set_elevation("Open-Elevation")

#set properties of Nitrous
#TODO set density correctly for temp
liquid_N2O = rocketpy.Fluid(name="Liquid Nitrous Oxide", density=855)

#properties of nitrogen, density at 18°C and 50 bar
vapour_N = rocketpy.Fluid(name="Gaseous Nitrogen", density=58)

#set tank size
N2O_geometry = rocketpy.CylindricalTank(radius=0.138/2, height=0.545, spherical_caps=False)

#tank
N2O_tank = rocketpy.MassBasedTank(
    name = "Nitrous_Oxide_Tank",
    geometry = N2O_geometry,
    flux_time = 25,
    gas = vapour_N,
    liquid = liquid_N2O,
    gas_mass = N2O_geometry.volume*0.1*vapour_N.density,
    liquid_mass = 4.7,
    discretize=100,
)

#MOTOR
#TODO fix all of this
hyacinth_motor = rocketpy.HybridMotor(
    thrust_source=lambda t: 2500,
    dry_mass=4.5,
    #TODO inertia
    dry_inertia=(0.125, 0.125, 0.002),
    nozzle_radius=28.9e-3,
    grain_number=1,
    grain_separation=0,
    grain_outer_radius=0.057,
    grain_initial_inner_radius=0.0275,
    grain_initial_height=0.250,
    grain_density=900,
    grains_center_of_mass_position=0.245,
    #TODO figure actual CoG out
    center_of_dry_mass_position=0.245,
    nozzle_position=0,
    burn_time=5,
    throat_radius=0.015,
)

hyacinth_motor.add_tank(
    tank=N2O_tank,
    position=1, #TODO
)

#definition of values for inertia calculation; inertia calculation based on ideal cylinder
#TODO change to actual parts, import from valispace
height = 3.22
mass = 23.727
radius=0.076

hyacinth = rocketpy.Rocket(
    radius=radius,
    mass=mass,
    #TODO fix inertia
    inertia=((mass/2)*0.5*(radius**2+(height**2/3)), (mass/2)*0.5*(radius**2+(height**2/3)), (mass/2)*radius**2),
    power_off_drag="data/drag/FrodoMPowerOffDrag.csv", #obtained using RasAero #TODO redo
    power_on_drag="data/drag/FrodoMPowerOnDrag.csv", #obtained using RasAero
    center_of_mass_without_motor=1.54, #coordinate system same as OpenRocket and RasAero #TODO recalculate
    coordinate_system_orientation="nose_to_tail"
)

buttons = hyacinth.set_rail_buttons(
    upper_button_position=1.90, #TODO
    lower_button_position=2.95, #TODO
)

hyacinth.add_motor(hyacinth_motor, position=3.22)
#add von karman nose cone

hyacinth.add_nose(
    length=0.45,
    kind="von karman",
    position=0,
)

#add fin set
hyacinth.add_trapezoidal_fins(
    n=3,
    root_chord=0.240,
    tip_chord=0.160,
    span=0.150,
    position=2.87,
    sweep_length=0.060,
    airfoil=None #TODO make airfoil (0008)
)

#add boattail
hyacinth.add_tail(
    top_radius=0.076,  
    bottom_radius=0.06,
    length=0.10, 
    position=3.12
)

#add main chute, values according to fruity chutes
hyacinth.add_parachute(
    name="main",
    cd_s=2.2*math.pi*0.914**2,
    trigger=400,
    sampling_rate=105,
    lag=0.1,
    noise=(0,0,0) #TODO
)

#add drogue chute, values according to fruity chutes 
#TODO change to whatever we are doing
hyacinth.add_parachute(
    name="drogue",
    cd_s=1.5*math.pi*0.305**2,
    trigger="apogee",
    sampling_rate=105,
    lag=1,
    noise=(0,0,0) #TODO
)

#define launch, values according to Euroc
euroc2025 = rocketpy.Flight(
        environment=launch_environment,
        rocket=hyacinth,
        rail_length=12,
        inclination=84,
        heading=133,
        )


#PRINTS AND PLOTS
launch_environment.prints.launch_site_details()

#printing values
euroc2025.prints.maximum_values()

euroc2025.prints.out_of_rail_conditions()

euroc2025.prints.apogee_conditions()

euroc2025.prints.impact_conditions()

euroc2025.prints.events_registered()

#plotting values
hyacinth.plots.static_margin()

hyacinth.draw()

euroc2025.plots.trajectory_3d()

euroc2025.plots.linear_kinematics_data()