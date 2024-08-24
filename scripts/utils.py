def transform_to_jsonl(data):
    transformed_data = []

    if isinstance(data, dict):
        lxGroups = data.get("lxGroup", [])

        # Convert lxGroups to a list if it's a single object
        if isinstance(lxGroups, dict):
            lxGroups = [lxGroups]

        for lxGroup in lxGroups:
            if isinstance(lxGroup, dict):
                psGroup = lxGroup.get("psGroup", {})
                if isinstance(psGroup, dict):
                    geGroup = psGroup.get("geGroup", {})
                    if isinstance(geGroup, dict):
                        xvGroup = geGroup.get("xvGroup", [])

                        if isinstance(xvGroup, dict):
                            xvGroup = [xvGroup]

                        if isinstance(xvGroup, list):
                            if lxGroup.get("lx", "") and geGroup.get("ge", ""):
                                transformed_data.append(
                                    {
                                        "input": lxGroup.get("lx", ""),
                                        "output": {
                                            "definition": geGroup.get("ge", "")
                                            if "ge" in geGroup
                                            else "",
                                            "etymology": lxGroup.get("etGroup", {}).get(
                                                "et", ""
                                            )
                                            if "et" in lxGroup.get("etGroup", {})
                                            else "",
                                            "synonym": psGroup.get("sy", {})
                                            if "sy" in psGroup
                                            else "",
                                        },
                                    }
                                )

                            for entry in xvGroup:
                                xv = entry.get("xv", "")
                                xe = entry.get("xe", "")
                                if xv and xe:
                                    transformed_data.append({"input": xv, "output": xe})
    print(f"Données transformées: {transformed_data}")  # Débogage
    return transformed_data
