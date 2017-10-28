import os
import json
import time

db_path = "/nfs-6/userdata/bemarsh/CSC_DQM/Run2017/SingleMuon"
database = os.listdir(db_path)

db_map = {"newest":0, "timestamp":0, "files":{}}

newest = 0
for f in database:
    last_mod = os.path.getmtime("{0}/{1}".format(db_path, f))
    if last_mod > newest:
        newest = last_mod

    db_map["files"][f.split(".root")[0]] = last_mod

db_map["newest"] = newest
db_map["timestamp"] = time.time()

with open("{0}/db_map.json".format(os.getcwd()), "w") as fhout:
    json.dump(db_map, fhout, sort_keys = True, indent = 4, separators = (',',':'))
