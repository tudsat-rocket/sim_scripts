import rocketpy

import datetime
import math

import libs.data_handler as data_handler

#TODO fix drymasses for tank/motor by getting from valispace or setting to 0

#FILES
drag_pwr_off = "Hyacinth/rocketpy/data/drag/HyacinthPowerOffDrag.csv"
drag_pwr_on = "Hyacinth/rocketpy/data/drag/HyacinthPowerOnDrag.csv"
fin_lift = "Hyacinth/rocketpy/data/lift/naca_0008_final.csv"

valispace_data = data_handler.load_data("Hyacinth/rocketpy/data/valispace/vali_sim_data.yaml")

#euroc launch site
launch_environment = rocketpy.Environment(
    latitude = valispace_data["LaunchEnvironment"]["latitude"],
    longitude = valispace_data["LaunchEnvironment"]["longitude"],
    elevation = valispace_data["LaunchEnvironment"]["elevation"]
)

#time within competition time frame (09/10-15/10, launches likely 10/10-14/10)
launch_environment.set_date(
    (2025, 10, 12, 12), timezone="Europe/Lisbon"
)

#sample wind and temperature based on historical data
launch_environment.set_atmospheric_model(
    type="custom_atmosphere",
    pressure=None,
    temperature=None,
    #TODO change this to historical wind
    #TODO potential pressure and temperature with custom atmosphere
    wind_u = -1.5,
    wind_v = -0.5,
)

#currently unused: OpenElevation for elevation data
#launch_environment.set_elevation("Open-Elevation")

#set properties of Nitrous
#TODO set density correctly for temp
liquid_N2O = rocketpy.Fluid(name="Liquid Nitrous Oxide", density = valispace_data["NitrousOxide"]["density"])

#properties of nitrogen, density at 18°C and 50 bar
#TODO get correct density or switch model to not use constant density
vapour_N = rocketpy.Fluid(name="Gaseous Nitrogen", density=58)

#set tank size
N2O_geometry = rocketpy.CylindricalTank(radius = valispace_data["OxidizerTank"]["inner_diameter"]/2, height = valispace_data["OxidizerTank"]["inner_height"], spherical_caps=False)

#tank
N2O_tank = rocketpy.MassFlowRateBasedTank(
    name = "Nitrous_Oxide_Tank",
    geometry = N2O_geometry,
    flux_time = 5,
    gas = vapour_N,
    liquid = liquid_N2O,
    initial_gas_mass = 0, #N2O_geometry.volume*0.1*vapour_N.density
    initial_liquid_mass = valispace_data["NitrousOxide"]["mass_oxidizer"],
    liquid_mass_flow_rate_in = 0,
    liquid_mass_flow_rate_out = valispace_data["NitrousOxide"]["mass_oxidizer"]/valispace_data["C_Propulsion_Module"]["time_burn"],
    gas_mass_flow_rate_in = 0,
    gas_mass_flow_rate_out = 0,
    discretize=100,
)

#MOTOR
#TODO fix all of this
hyacinth_motor = rocketpy.HybridMotor(
    thrust_source=lambda t: valispace_data["C_Propulsion_Module"]["thrust"]-t*120,
    dry_mass=valispace_data["Nitrogen"]["mass_pressurant"], #temporarily adding mass of nitrogen here
    dry_inertia=(0, 0, 0),
    nozzle_radius=valispace_data["Nozzle"]["exit_diameter"]/2,
    grain_number=1,
    grain_separation=0,
    grain_outer_radius=valispace_data["SolidFuel"]["outer_diameter"]/2,
    grain_initial_inner_radius=valispace_data["SolidFuel"]["inner_diameter"]/2,
    grain_initial_height=valispace_data["SolidFuel"]["length"],
    grain_density=valispace_data["SolidFuel"]["density"],
    grains_center_of_mass_position=0.245, #TODO define and import this
    #TODO figure actual CoG out, check mass
    center_of_dry_mass_position=1.5, #temporarily changed to roughly represent com of nitrogen
    nozzle_position=0,
    burn_time=valispace_data["C_Propulsion_Module"]["time_burn"],
    throat_radius=valispace_data["Nozzle"]["throat_diameter"]/2,
)

hyacinth_motor.add_tank(
    tank=N2O_tank,
    position=1, #TODO import this
)

#TODO add nitrogen tank

#definition of values for inertia calculation; inertia calculation based on ideal cylinders
height = valispace_data["Rocket"]["length"]
mass = valispace_data["Rocket"]["mass"]
com = data_handler.center_of_mass(valispace_data)
radius = valispace_data["Rocket"]["radius"]
inertia_axial, inertia_radial = data_handler.inertia(valispace_data, com, radius)

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
    upper_button_position=1.90, #TODO import this
    lower_button_position=2.95, #TODO import this
)

hyacinth.add_motor(hyacinth_motor, position=height)

#add von karman nose cone
hyacinth.add_nose(
    length=0.45,#TODO import this
    kind="von karman",
    position=0,
)

#add fin set
hyacinth.add_trapezoidal_fins(
    n=3,
    root_chord=valispace_data["FinCan"]["fins_root_chord"],
    tip_chord=valispace_data["FinCan"]["fins_tip_chord"],
    span=valispace_data["FinCan"]["fins_span"],
    position=height-valispace_data["FinCan"]["fins_root_chord"],
    sweep_length=valispace_data["FinCan"]["fins_sweep_length"],
    airfoil=(fin_lift,"degrees")
)

#add boattail
hyacinth.add_tail(
    top_radius=radius,
    bottom_radius=valispace_data["FinCan"]["boattail_bottom_radius"],
    length=valispace_data["FinCan"]["boattail_length"],
    position=height-valispace_data["FinCan"]["boattail_length"]
)

#add main chute, values according to fruity chutes
#TODO define and import
hyacinth.add_parachute(
    name="main",
    cd_s=2.2*math.pi*0.914**2,
    #cd_s=2.2*math.pi*(2.1336/2)**2,
    trigger=400,
    sampling_rate=105,
    lag=0.1,
    noise=(0,0,0)
)

#add drogue chute, values according to fruity chutes
#TODO change to whatever we are doing
hyacinth.add_parachute(
    name="drogue",
    cd_s=1.5*math.pi*0.305**2,
    trigger="apogee",
    sampling_rate=105,
    lag=1,
    noise=(0,0,0)
)

#define launch, values according to Euroc
euroc2025 = rocketpy.Flight(
        environment=launch_environment,
        rocket=hyacinth,
        rail_length=valispace_data["LaunchEnvironment"]["rail_length"],
        inclination=valispace_data["LaunchEnvironment"]["inclination"],
        heading=valispace_data["LaunchEnvironment"]["heading"],
        )


#PRINTS AND PLOTS
#launch_environment.prints.launch_site_details()

#printing values
if True:
    euroc2025.prints.maximum_values()

    euroc2025.prints.out_of_rail_conditions()

    euroc2025.prints.apogee_conditions()

    euroc2025.prints.impact_conditions()

    euroc2025.prints.events_registered()

    hyacinth.prints.inertia_details()

    #hyacinth.all_info()
#plotting values
if True:
    hyacinth.plots.static_margin()

    hyacinth.draw()

    #euroc2025.plots.trajectory_3d()

    euroc2025.plots.linear_kinematics_data()

    hyacinth.plots.total_mass()
