import json
import os

def bump(version, bump_type):
    parts = version.strip().split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    if bump_type == "major":
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"

bump_type = os.environ.get("BUMP_TYPE", "patch")

with open("versions.json", "r", encoding="utf-8") as f:
    vdata = json.load(f)

old_version = vdata["version"].strip()
new_version = bump(old_version, bump_type)
vdata["version"] = new_version

with open("versions.json", "w", encoding="utf-8") as f:
    json.dump(vdata, f, indent=2)

with open("package.json", "r", encoding="utf-8") as f:
    pdata = json.load(f)

pdata["version"] = new_version

with open("package.json", "w", encoding="utf-8") as f:
    json.dump(pdata, f, indent=2)

# Write with no newline and no hidden characters
with open("NEW_VERSION.txt", "w", encoding="utf-8", newline='') as f:
    f.write(new_version)

print(f"NEW_VERSION={new_version}")
print(f"Bumped {old_version} -> {new_version}")
