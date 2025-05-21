"""

Valispace API retriever

put your username a.k.a. email in line 30

install libraries with
    "pip install valispace"
    "pip install pyyaml"


More info on API:
https://github.com/valispace/ValispacePythonAPI



"""

import valispace

import getpass

import yaml

import datetime

#LOGIN

username = input("Enter valispace username: ")

valispace = valispace.API(url='https://tudsat.valispace.com', username=username , password=getpass.getpass("Enter valispace password: "))

date_string = "{:%Y%m%d_%H%M%S}".format(datetime.datetime.now())

#GET COMPONENTS
components = valispace.get_component_list(project_name = "Hyacinth")

allowed_keys_components = ["name", "id", "description", "unique_name",
                           "parent", "children","linked_requirements", "verified_requirement_vms", "total_requirement_vms", "verified",
                           "is_alternative_container", "current_alternative", "alternatives"]

filtered_components = {component["unique_name"]: {key: component[key] for key in component.keys() if key in allowed_keys_components} for component in components}


with open(date_string+"_vali_comps.yaml", "w", encoding="utf-8") as file:
    yaml.dump(filtered_components, file)


#GET VALIS
valis = valispace.get_vali_list(project_name="Hyacinth")

allowed_keys_valis = ["path", "id", "description", "shortname", "parent",
                      "value", "unit", "wc_plus", "wc_minus", "formula", "latex_formula",
                      "margin_minus", "margin_plus", "totalmargin_plus", "totalmargin_minus"]

filtered_valis = {vali["path"]+"."+vali["shortname"]: {key: vali[key] for key in vali.keys() if key in allowed_keys_valis} for vali in valis}

with open(date_string+"_vali_valis.yaml", "w", encoding="utf-8") as file:
    yaml.dump(filtered_valis, file)

#GET REQUIREMENTS
spec_folders = valispace.get_folders(project_id=42)
allowed_keys_folders = ["id", "name", "items"]
spec_folders = [{key: folder[key] for key in folder.keys() if key in allowed_keys_folders} for folder in spec_folders]

specifications = valispace.get_specifications(project_id=42)
allowed_keys_specifications = ["name", "id", "abbr", "components", "description", "requirement_groups", "requirements"]
specifications = [{key: spec[key] for key in spec.keys() if key in allowed_keys_specifications} for spec in specifications]

req_groups = valispace.get_groups(project_id=42)
allowed_keys_groups = ["id", "name", "specification", "requirements", "description"]
req_groups = [{key: group[key] for key in group.keys() if key in allowed_keys_groups} for group in req_groups]

requirements = valispace.get_requirements(project_id=42)
allowed_keys_requirements = ["title", "identifier", "specification", "id", "group",
                             "linked_components",  "verification_items", "verification_methods", "verified", 
                             "rationale", "text",]
requirements = [{key: req[key] for key in req.keys() if key in allowed_keys_requirements} for req in requirements]

#req->req_vm->comp_vm comp vms actually do stuff
req_vms = valispace.get(url="requirements/requirement-vms/", data={"project": "42"})

comp_vms = valispace.get(url="requirements/component-vms/", data={"project": "42"})

vms = valispace.get(url="requirements/verification-methods/", data={"project": "42"})

with open(date_string+"_vali_vms.yaml", "w", encoding="utf-8") as file:
    yaml.dump(vms, file)

req_tree_dict = {folder["name"]: 
                {spec["name"]:
                    {"requirements": {req["identifier"]: req["id"] for req in requirements if req["id"] in spec["requirements"]},
                     "groups": {group["name"]:
                        {req["identifier"]: req["id"] for req in requirements if req["id"] in group["requirements"]}
                    for group in req_groups if group["id"] in spec["requirement_groups"]}}
                for spec in specifications if spec["id"] in folder["items"]}
            for folder in spec_folders}

with open(date_string+"_vali_req_grps.yaml", "w", encoding="utf-8") as file:
    yaml.dump(req_tree_dict, file)

req_dict = {req["identifier"]: req for req in requirements}

with open(date_string+"_vali_reqs.yaml", "w", encoding="utf-8") as file:
    yaml.dump(req_dict, file)

#EXAMPLE LOAD
#with open("output.yaml", "r", encoding="utf-8") as file:
    #test = yaml.safe_load(file).values()