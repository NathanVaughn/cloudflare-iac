import json

# pulumi stack export --stack prod > stack.json

with open("stack.json", "r") as fp:
    data = json.load(fp)

with open("delete.sh", "w") as fp:
    # write the shebang
    fp.write("#!/bin/bash\n\n")

    resources = data["deployment"]["resources"]
    resources.reverse()

    for resource in resources:
        urn = resource["urn"]
        # if "lksg" not in urn:
        #     continue

        fp.write(f"echo 'Deleting {urn}'\n")
        fp.write(f"pulumi state delete {urn} --yes\n")
