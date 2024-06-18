from rocketpy import Environment, Rocket, SolidMotor, Flight

import datetime
import math

launch_environment = Environment(
    latitude = 39.39011270334382,
    longitude = -8.28928771347388,
    elevation = 123.9,
)

launch_environment.set_date(
    (2024, 10, 12, 12), timezone="Europe/Lisbon"
)

#launch_environment.set_atmospheric_model(type="Forecast", file="GFS")
launch_environment.set_atmospheric_model(
    type="custom_atmosphere",
    pressure=None,
    temperature=273.15+21,
    wind_u = [(0,-1.5), (1000, -5)],
    wind_v = [(0,-0.5), (1000, -2)],
)

motor_m1790 = SolidMotor(
    thrust_source="data/motors/Cesaroni_8088M1790-P.eng",
    dry_mass=3.567,
    dry_inertia=(0.125, 0.125, 0.002),#sample values, idk
    center_of_dry_mass_position=0.3, #just a bad guess
    grains_center_of_mass_position=0.35, #an even worse guess
    burn_time=4.5,
    grain_number = 4,
    grain_separation=0.005,#idk
    grain_density=1815,#idk
    grain_outer_radius=0.046,
    grain_initial_inner_radius=0.020,
    grain_initial_height=0.13,
    nozzle_radius=0.039,
    throat_radius=0.013,
    interpolation_method="linear",
    coordinate_system_orientation="nozzle_to_combustion_chamber"
)

height = 3.015
mass = 15.245
radius=0.075

# Regarding calculation of intertia c.f. https://itp.uni-frankfurt.de/~luedde/Lecture/Mechanik/Intranet/Skript/Kap7/node5.html
frodo_m = Rocket(
    radius=radius,
    mass=mass,
    inertia=((mass/2)*0.5*(radius**2+(height**2/3)), (mass/2)*0.5*(radius**2+(height**2/3)), (mass/2)*radius**2),
    power_off_drag=None, #TODO
    power_on_drag=None, #TODO
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose"
)

buttons = frodo_m.set_rail_buttons(
    upper_button_position=0, #TODO
    lower_button_position=0, #TODO
)

frodo_m.add_motor(motor_m1790, 
        position=0 #TODO
        )

nose_cone = frodo_m.add_nose(
    length=0, #TODO,
    kind="von karman",
    position=0, #TODO
)

#TODO
fin_set = frodo_m.add_trapezoidal_fins(
    n=4,
    root_chord=0.120,
    tip_chord=0.060,
    span=0.110,
    position=-1.04956,
    cant_angle=0.5,
    airfoil=("../data/calisto/NACA0012-radians.csv","radians"),
)

# TODO
tail = frodo_m.add_tail(
    top_radius=0.0635,  
    bottom_radius=0.0435,
    length=0.060, 
    position=-1.194656
)

main = frodo_m.add_parachute(
    name="main",
    cd_s=2.2*math.pi*1.22**2,
    trigger=450,
    sampling_rate=105,
    lag=1, #TODO
    noise=(0,0,0) #TODO
)

drogue = frodo_m.add_parachute(
    name="drogue",
    cd_s=1.6*math.pi*0.3**2,
    trigger="apogee",
    sampling_rate=105,
    lag=1, #TODO
    noise=(0,0,0) #TODO
)

frodo_m.plots.static_margin()

frodo_m.draw()

euroc = Flight(
        environment=launch_environment,
        rocket=frodo_m,
        rail_length=6, #TODO
        inclination=85,
        heading=0 #TODO
        )

euroc.prints.maximum_values()

euroc.plots.trajectory_3d()

euroc.plots.linear_kinematics_data()

