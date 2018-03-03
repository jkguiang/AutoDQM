import os
import sys
import json
import time
import fetch

from tqdm import tqdm 

cmd = sys.argv[1] # commands: build->(get samples, populate database), map->(populate/update database map)

# Path to directory containing all data
main_dir = os.path.dirname(os.path.dirname(os.getcwd()))

# populate/update database map
def map_db():
    db_map = {"newest":0, "timestamp":0, "files":{}}

    # Populate database map
    for sample in samples:
        db_map["files"][sample] = {}

        db_path = "{0}/data/database/Run{1}/{2}".format(main_dir, year, sample)
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
    # User input loop
    while True:
        print("Enter the number of files you would like downloaded (starting from the newest DQM file).")
        print("If you would like to download ALL files, enter 'all'")
        limit_inp = raw_input("Input: ")
        if limit_inp == "all":
            print("\nWARNING: This process may take some time.")
            confirm = raw_input("Continue? y/n: ")
            if confirm == "y":
                limit = False
                break
            else:
                print("\n")
                continue
        else:
            try:
                limit = int(limit_inp)
                break
            except ValueError:
                print("ERROR: Please enter a number or 'all'.\n")
                continue

    # Load configs
    with open("{0}/data/configs.json".format(main_dir)) as config_file:
        config = json.load(config_file)
    samples = config["samples"]
    year = config["year"]

    # Build directory structure
    db_dir = "{0}/data/database/Run{1}".format(main_dir, year)
    if not os.path.isdir(db_dir):
        print("Created {0}".format(db_dir))
        os.mkdir(db_dir, 0755)

    print("Building database...")
    for sample in tqdm(samples):
        files_found = 0
        # Make directory for sample
        sample_dir = "{0}/data/database/Run{1}/{2}".format(main_dir, year, sample)
        if not os.path.isdir(sample_dir):
            tqdm.write("Created {0}".format(sample_dir))
            os.mkdir(sample_dir)

        # Get list of runs
        tqdm.write("Retrieving list of runs...")
        runs = fetch.get_runs(limit, str(year), sample)
        tqdm.write("Retrieved list of runs.")

        # Fetch runs
        tqdm.write("Downloading files...")
        for i in tqdm(range(0, limit)):
            run = runs[i]
            is_success, fail_reason = fetch.fetch(str(run), sample)
            if not is_success:
                tqdm.write("ERROR: {0}".format(fail_reason))
                return
            else:
                files_found += 1

        tqdm.write("Finished combing {0}. Found: {1}/{2}".format(sample, files_found, limit))
    print("Finished building database.")
    return

if __name__ == "__main__":
    if cmd == "map": map_db()
    elif cmd == "build": build_db()
