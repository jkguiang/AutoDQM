import os
import sys
import json
import time

cmd = sys.argv[1] # commands: build->(get samples, populate database), map->(populate/update database map)
samples = ["SingleMuon", "Cosmics"] #WIP
cur_subsys = sys.argv[2] # subsystem acronym passed in from setup.sh
year = 2017 # run year
db_map = {"newest":0, "timestamp":0, "files":{}}

# populate/update database map
def map():
    # Populate database map
    for sample in samples:
        db_map["files"][sample] = {}

        db_path = "/{0}_db/Run{1}/{2}".format(cur_subsys, year, sample)
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

    # Ensure database map has proper permissions
    os.system("chmod 755 db_map.json")

    return

# get samples, populate/structure database
def build():

if cmd == "map": map()
elif cmd == "build": build()
