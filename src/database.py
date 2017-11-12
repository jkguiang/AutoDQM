import os
import json
import time

samples = ["SingleMuon", "Cosmics"]
db_map = {"newest":0, "timestamp":0, "files":{}}

# Populate database map
for sample in samples:
    db_map["files"][sample] = {}

    db_path = "/nfs-6/userdata/bemarsh/CSC_DQM/Run2017/{0}".format(sample)
    database = os.listdir(db_path)

    newest = 0
    for f in database:
        last_mod = os.path.getmtime("{0}/{1}".format(db_path, f))
        if last_mod > newest:
            newest = last_mod

        db_map["files"][sample][f.split(".root")[0]] = last_mod

    db_map["newest"] = newest

# Update database map timestamp
db_map["timestamp"] = time.time()

# Dump database map into json
with open("{0}/db_map.json".format(os.getcwd()), "w") as fhout:
    json.dump(db_map, fhout, sort_keys = True, indent = 4, separators = (',',':'))
