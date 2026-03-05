import yaml

#Loads valispace output from yaml file at "location"
#returns dictionary of data contained
def load_data(location):

    out = {}
    with open(location, "r", encoding="utf-8") as file:
        out = yaml.safe_load(file)

    return out

def center_of_mass(data):
    mass_radius_sum = 0
    mass_sum = 0

    for child in data["components"].values():
        child_mass_sum, child_mass_radius_sum = com_rec(child)
        mass_sum += child_mass_sum
        mass_radius_sum += child_mass_radius_sum

    return mass_radius_sum/mass_sum

def com_rec(comp):
    #calulate own mass and mass * radius
    if comp["children"] == {}:
        return (comp["valis"]["mass"], comp["valis"]["mass"] * (comp["valis"]["position"] + comp["valis"]["length"]/2))
    #if children, use them instead
    else:
        mass_sum = 0
        mass_radius_sum = 0
        for child in comp["children"].values():
            child_mass_sum, child_mass_radius_sum = com_rec(child)
            mass_sum += child_mass_sum
            mass_radius_sum += child_mass_radius_sum

        #report mass mismatches
        if abs(mass_sum - comp["valis"]["mass"]) > 0.001:
            print(f"Mass mismatch in data: component {comp['name']} mass {comp['valis']['mass']} kg, children mass sum {mass_sum} kg")
        return (mass_sum, mass_radius_sum)


def inertia(data, com, radius):
    inertia_axial = 0
    inertia_radial = 0

    for comp in data["components"].values():
        comp_in_ax, comp_in_rad = inertia_rec(comp, com, radius)
        inertia_axial += comp_in_ax
        inertia_radial += comp_in_rad

    return (inertia_axial, inertia_radial)

def inertia_rec(comp, com, radius):

    if comp["children"] == {}:
        comp_length = comp["valis"]["length"]
        comp_com = comp["valis"]["position"] + (comp["valis"]["length"]/2)
        comp_mass = comp["valis"]["mass"]

        #axial inertia (cylinder)
        in_ax = 0.5 * comp_mass * radius**2

        #radial inertia (cylinder)
        in_rad = (radius**2/4 + comp_length**2/12) * comp_mass

        #parallel axis theorem
        in_rad += comp_mass * abs(comp_com-com)**2

    else:
        in_ax = 0
        in_rad = 0

        for child in comp["children"].values():
            child_in_ax, child_in_rad = inertia_rec(child, com, radius)
            in_ax += child_in_ax
            in_rad += child_in_rad

    return (in_ax, in_rad)

