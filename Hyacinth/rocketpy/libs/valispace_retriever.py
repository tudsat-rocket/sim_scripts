"""

Valispace API retriever for Sim



install libraries with
    "pip install valispace"
    "pip install yaml"


More info on API:
https://github.com/valispace/ValispacePythonAPI



"""

import valispace

import getpass

import yaml

import datetime

allowed_keys_sim = ["length", "mass", "position"]

extra_info = {"LaunchEnvironment": ["latitude", "longitude", "elevation", "rail_length", "inclination", "heading"],
              "Rocket": ["length", "mass", "radius"],
              "C_Propulsion_Module": ["thrust", "time_burn"],
              "SolidFuel": ["mass_fuel", "outer_diameter", "inner_diameter", "length", "density"],
              "FinCan": ["fins_root_chord", "fins_tip_chord", "fins_span", "fins_sweep_length", "boattail_bottom_radius", "boattail_length"],
              "NitrousOxide": ["density", "mass_oxidizer"],
              "OxidizerTank": ["inner_height", "inner_diameter"],
              "Nitrogen": ["mass_pressurant"]}

conversion_factors = {"mm": 1e-3, "cm": 1e-2, "dm": 1e-1, "m": 1, "km": 1e3,
                      "mg": 1e-6, "g": 1e-3, "kg": 1, "t": 1e3,
                      "ms": 1e-3, "s": 1, "min": 60, "h": 3600, "d": 86400,
                      "mN": 1e-3, "N": 1, "kN": 1e3,
                      "g/cm³": 1e3, "g/cm^3": 1e3, "kg/m³": 1, "kg/m^3": 1,
                      "deg": 1,
                      "": 1}

#converts units into SI base units
def clean_units(value, unit):
    conv_factor = 1
    if unit in conversion_factors:
        conv_factor = conversion_factors[unit]
    else:
        print(f"Unknown unit, assuming SI compliant: {unit}")

    return value*conv_factor

#gets valis for a component with a certain id
def get_valis(id):
    return {vali["shortname"]: clean_units(vali["value"], vali["unit"]) for vali in sim_valis if vali["parent"] == id and vali["shortname"] in allowed_keys_sim}

#builds component tree recursively
def get_rec_components(id):
    current_comp = sim_comps[id]

    children = {child: get_rec_components(child) for child in current_comp["children"]}

    return {"name": current_comp["name"], "valis": get_valis(id), "children": children}

#makes sure every component has mass, position and length
#as well as making position absolute
def make_pos_abs(comp, parent_pos, parent_length):
    #get cases where pos and/or length aren't defined
    #presumed position is centered within parent and length 0
    if "position" in comp["valis"]:
        current_pos = parent_pos + comp["valis"]["position"]
    elif "length" in comp["valis"]:
        current_pos = parent_pos + parent_length/2 - comp["valis"]["length"]/2
    else:
        current_pos = parent_pos + parent_length/2

    if "length" in comp["valis"]:
        current_length = comp["valis"]["length"]
    else:
        current_length = 0

    #good old recursion
    for child_comp in comp["children"].values():
        make_pos_abs(child_comp, current_pos, current_length)

    comp["valis"]["position"] = current_pos
    comp["valis"]["length"] = current_length

    if not "mass" in comp["valis"]:
        comp["valis"]["mass"] = 0

#LOGIN
username = input("Enter valispace username: ")

hidden_input = getpass.getpass("Enter valispace password: ")

pwd = hidden_input

valispace = valispace.API(url='https://tudsat.valispace.com', username=username , password=pwd)

#date_string = "{:%Y%m%d_%H%M%S}".format(datetime.datetime.now())

#GET COMPONENTS
components = valispace.get_component_list(project_name = "Hyacinth")

allowed_keys_components = ["name", "id", "description", "unique_name",
                           "parent", "children","linked_requirements", "verified_requirement_vms", "total_requirement_vms", "verified",
                           "is_alternative_container", "current_alternative", "alternatives"]

sim_comps = {component["id"]: {key: component[key] for key in component.keys() if key in allowed_keys_components} for component in components}

#GET VALIS
valis = valispace.get_vali_list(project_name="Hyacinth")

allowed_keys_valis = ["path", "id", "description", "shortname", "parent",
                      "value", "unit", "wc_plus", "wc_minus", "formula", "latex_formula",
                      "margin_minus", "margin_plus", "totalmargin_plus", "totalmargin_minus"]

sim_valis = [{key: vali[key] for key in vali.keys() if key in allowed_keys_valis} for vali in valis]

#CLEANUP
out_dict = get_rec_components(4256)
out_dict["valis"]["position"] = 0

make_pos_abs(out_dict, 0, 0)

out_dict.pop("valis")
out_dict["components"] = out_dict.pop("children")
out_dict.pop("name")

#ADD EXTRA INFO
for comp_name in extra_info:
    comp_id = [cmp["id"] for cmp in sim_comps.values() if cmp["name"] == comp_name][0]
    comp_valis = {vali["shortname"]: clean_units(vali["value"], vali["unit"]) for vali in sim_valis if vali["parent"] == comp_id and vali["shortname"] in extra_info[comp_name]}
    out_dict[comp_name] = comp_valis

#WRITE
with open("Hyacinth/rocketpy/data/valispace/vali_sim_data.yaml", "w", encoding="utf-8") as file:
    yaml.dump(out_dict, file)

date_string = "{:%Y%m%d_%H%M%S}".format(datetime.datetime.now())

with open("Hyacinth/rocketpy/data/valispace/" + date_string + "_vali_sim_data.yaml", "w", encoding="utf-8") as file:
    yaml.dump(out_dict, file)

    print("Successfully retrieved data.")
