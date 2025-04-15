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

    for module in data["children"].values():
        module_position = module["valis"]["position"]
        for submodule in module["children"].values():
            #position realative to parent module, length/2 is center of submodule
            submodule_com = module_position + submodule["valis"]["position"] + (submodule["valis"]["length"]/2)
            submodule_mass = submodule["valis"]["mass"]
            mass_radius_sum += submodule_com * submodule_mass
            mass_sum += submodule_mass

    #Check for valispace errors
    if abs(mass_sum - data["valis"]["mass"]) > 0.001:
        print(f"Mass mismatch in data: rocket mass {data['valis']['mass']} kg, submodule mass sum {mass_sum} kg")

    return mass_radius_sum/mass_sum

def inertia(data, com, radius):
    inertia_short = 0
    inertia_long = 0

    for module in data["children"].values():
        module_position = module["valis"]["position"]
        for submodule in module["children"].values():
            submodule_length = submodule["valis"]["length"]
            submodule_com = module_position + submodule["valis"]["position"] + (submodule_length/2)
            submodule_mass = submodule["valis"]["mass"]
            #add cylinder inertia along axis to short inertia
            inertia_short += 0.5 * submodule_mass * radius**2

            #add cylinder inertia perpendicular to axis to long inertia
            inertia_long += (radius**2/4 + submodule_length**2/12)*submodule_mass

            #add steinerscher bullshit to long inertia
            inertia_long += submodule_mass * abs(submodule_com-com)**2

    return (inertia_short, inertia_long)

