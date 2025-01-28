# Transform the given nested JSON into a flattened array format

# Transform the given nested JSON into a flattened array format

import json

# Original JSON data
with open("data/wiki/sharks/angel_sharks.json", "r", encoding="utf-8") as file:
    data1 = json.load(file)

with open("data/wiki/sharks/saw_sharks.json", "r", encoding="utf-8") as file:
    data2 = json.load(file)

# Flattening the JSON into a list of dictionaries
flattened = []

for family in data1["families"]:
    for genus in family["genera"]:
        for species in genus["species"]:
            flattened.append({
                "order": data1["order"],
                # "order_name": data1["name"],
                "family": family["name"],
                "family_common_name": family["common_name"],
                "genus": genus["name"],
                "genus_author": genus["author"],
                "species_name": species["scientific_name"],
                "species_author": species["author"],
                "species_common_name": species["common_name"],
            })

for family in data2["families"]:
    for genus in family["genera"]:
        for species in genus["species"]:
            flattened.append({
                "order": data2["order"],
                # "order_name": data2["name"],
                "family": family["name"],
                "family_common_name": family["common_name"],
                "genus": genus["name"],
                "genus_author": genus["author"],
                "species_name": species["scientific_name"],
                "species_author": species["author"],
                "species_common_name": species["common_name"],
            })

# Output the flattened JSON
with open("data/wiki/sharks/sharks.json", "w",  encoding="utf-8") as file:
    json.dump(flattened, file, indent=2, ensure_ascii=False)
