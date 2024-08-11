from rocketpy import Environment, Rocket, SolidMotor, Flight

import datetime
import math

#set environment to actual launch site
launch_environment = Environment(
    latitude = 39.39011270334382,
    longitude = -8.28928771347388,
    elevation = 123.9,
)

#set time to within competition time frame
launch_environment.set_date(
    (2024, 10, 12, 12), timezone="Europe/Lisbon"
)

#sample wind and temperature based on historical data
launch_environment.set_atmospheric_model(
    type="custom_atmosphere",
    pressure=None,
    temperature=273.15+25,
    wind_u = [(0,-1.5), (1000, -5)],
    wind_v = [(0,-0.5), (1000, -2)],
)

#define motor; values from official Cesaroni documents, sample code and own measurements
motor_m1545 = SolidMotor(
    thrust_source="data/motors/Cesaroni_8187M1545-P.eng",
    dry_mass=3.043,
    dry_inertia=(0.125, 0.125, 0.002),
    center_of_dry_mass_position=0.510,
    grains_center_of_mass_position=0.510,
    burn_time=5.3,
    grain_number = 6,
    grain_separation=0.005,
    grain_density=1953,
    grain_outer_radius=0.033,
    grain_initial_inner_radius=0.015,
    grain_initial_height=0.152,
    nozzle_radius=0.033,
    throat_radius=0.011,
    interpolation_method="linear",
    nozzle_position=0,
    coordinate_system_orientation="nozzle_to_combustion_chamber"
)

#definition of values for inertia calculation; inertia calculation based on ideal cylinder
height = 3.21
mass = 19
radius=0.076

frodo_m = Rocket(
    radius=radius,
    mass=mass,
    inertia=((mass/2)*0.5*(radius**2+(height**2/3)), (mass/2)*0.5*(radius**2+(height**2/3)), (mass/2)*radius**2),
    power_off_drag="data/drag/FrodoMPowerOffDrag.csv", #obtained using RasAero
    power_on_drag="data/drag/FrodoMPowerOnDrag.csv", #obtained using RasAero
    center_of_mass_without_motor=1.54, #coordinate system same as OpenRocket and RasAero
    coordinate_system_orientation="nose_to_tail"
)

buttons = frodo_m.set_rail_buttons(
    upper_button_position=1.90, #TODO
    lower_button_position=2.95, #TODO
)

frodo_m.add_motor(motor_m1545, 
        position=3.21
        )

#add von karman nose cone
nose_cone = frodo_m.add_nose(
    length=0.45,
    kind="von karman",
    position=0,
)

#add fin set
fin_set = frodo_m.add_trapezoidal_fins(
    n=3,
    root_chord=0.240,
    tip_chord=0.160,
    span=0.150,
    position=2.87,
    sweep_length=0.060,
    airfoil=None
)

#add boattail
tail = frodo_m.add_tail(
    top_radius=0.076,  
    bottom_radius=0.06,
    length=0.10, 
    position=3.11
)

#add main chute, values according to fruity chutes
main = frodo_m.add_parachute(
    name="main",
    cd_s=2.2*math.pi*0.914**2,
    trigger=400,
    sampling_rate=105,
    lag=0.1,
    noise=(0,0,0) #TODO
)

#add drogue chute, values according to fruity chutes
drogue = frodo_m.add_parachute(
    name="drogue",
    cd_s=1.5*math.pi*0.305**2,
    trigger="apogee",
    sampling_rate=105,
    lag=1,
    noise=(0,0,0) #TODO
)

#define launch, values according to Euroc
euroc = Flight(
        environment=launch_environment,
        rocket=frodo_m,
        rail_length=12,
        inclination=80,
        heading=150,
        )

#printing values
euroc.prints.maximum_values()

euroc.prints.out_of_rail_conditions()

euroc.prints.apogee_conditions()

euroc.prints.impact_conditions()

euroc.prints.events_registered()

#plotting values
frodo_m.plots.static_margin()

frodo_m.draw()

euroc.plots.trajectory_3d()

euroc.plots.linear_kinematics_data()