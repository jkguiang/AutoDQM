import os
import sys
import json
import time
import fetch

from tqdm import tqdm 

cmd = sys.argv[1] # commands: build->(get samples, populate database), map->(populate/update database map)
samples = ["SingleMuon", "Cosmics"] #WIP
year = 2017 # run year
db_map = {"newest":0, "timestamp":0, "files":{}}

# populate/update database map
def map_db():
    # Populate database map
    for sample in samples:
        db_map["files"][sample] = {}

        db_path = "{0}/database/Run{1}/{2}".format(os.getcwd(), year, sample)
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
def build_db():
    print("Building database...")
    start = 301531
    files_found = 0
    total = 0
    for sample in tqdm(samples):
        for run in tqdm(range(start, start+10)):
            total += 1
            is_success, fail_reason = fetch.fetch(str(run), str(year), sample, "")
            if is_success:
                files_found += 1

        print("Finished combing {0}. Found: {1}/{2}".format(sample, files_found, total))
    print("Finsihed.")
    return

if __name__ == "__main__":
    if cmd == "map": map_db()
    elif cmd == "build": build_db()
