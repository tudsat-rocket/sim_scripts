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

username = "manuel.schluesener@tudsat.space"

allowed_keys_sim = ["length", "mass", "position"]

def clean_units(value, unit, data_type):
    conv_factor = 1
    if data_type in ["position", "length"]:
        match unit:
            case "um":
                conv_factor = 1e-6
            case "mm":
                conv_factor = 1e-3
            case "cm":
                conv_factor = 1e-2
            case "dm":
                conv_factor = 1e-1
            case "m":
                conv_factor = 1
            case "km":
                conv_factor = 1e3
    elif data_type in ["mass"]:
        match unit:
            case "mg":
                conv_factor = 1e-6
            case "g":
                conv_factor = 1e-3
            case "kg":
                conv_factor = 1
            case "t":
                conv_factor = 1e3

    return value*conv_factor

def get_valis(id):
    return {vali["shortname"]: clean_units(vali["value"], vali["unit"], vali["shortname"]) for vali in sim_valis if vali["parent"] == id and vali["shortname"] in allowed_keys_sim}

def get_rec_components(id):
    current_comp = sim_comps[id]

    children = {child: get_rec_components(child) for child in current_comp["children"]}

    return {"name": current_comp["name"], "valis": get_valis(id), "children": children}


#LOGIN
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

out_dict = get_rec_components(4256)

with open("Hyacinth/data/valispace/vali_sim_data.yaml", "w", encoding="utf-8") as file:
    yaml.dump(out_dict, file)

date_string = "{:%Y%m%d_%H%M%S}".format(datetime.datetime.now())

with open("Hyacinth/data/valispace/" + date_string + "_vali_sim_data.yaml", "w", encoding="utf-8") as file:
    yaml.dump(out_dict, file)
