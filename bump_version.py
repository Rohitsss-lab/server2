import json
import os

def bump(version, bump_type):
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    if bump_type == "major":
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"

bump_type = os.environ.get("BUMP_TYPE", "patch")

with open("versions.json", "r") as f:
    vdata = json.load(f)

old_version = vdata["version"]
new_version = bump(old_version, bump_type)
vdata["version"] = new_version

with open("versions.json", "w") as f:
    json.dump(vdata, f, indent=2)

with open("package.json", "r") as f:
    pdata = json.load(f)

pdata["version"] = new_version

with open("package.json", "w") as f:
    json.dump(pdata, f, indent=2)

with open("NEW_VERSION.txt", "w") as f:
    f.write(new_version)

print(f"Bumped {old_version} -> {new_version}")
