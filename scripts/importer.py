import json

# pulumi stack export --stack prod > stack.json

with open("stack.json", "r") as fp:
    data = json.load(fp)

with open("import.sh", "w") as fp:
    # write the shebang
    fp.write("#!/bin/bash\n\n")

    for resource in data["deployment"]["resources"]:
        # skip items that do not have an id
        if "id" not in resource:
            continue

        id_ = resource["id"]
        type_ = resource["type"]
        name = resource["urn"].rsplit("::")[-1]

        if "zoneId" in resource["inputs"] and "Dnssec" not in type_:
            id_ = f"{resource['inputs']['zoneId']}/{id_}"

        # skip providers
        if "providers" in type_:
            continue

        # only do lksg resources
        # if "lksg" not in name:
        #     continue

        fp.write(f"pulumi import {type_} {name} {id_} --yes\n")
