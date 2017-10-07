import os
import sys
import time
import json
import test

def handle_main(args):
        short = False
        datasets = test.list_of_datasets(args["cron"], short)
        try:
            with open("{0}/new_files.json".format(os.getcwd()), "r") as fhin:
                cur_database = json.load(fhin)
        except ValueError:
            cur_database = {"newest":time.time()}

        to_write = []

        for ds in datasets:
            dsname = ds["dataset"]
            print(dsname)
            files = test.get_dataset_files(dsname)
            file_dict = test.filelist_to_dict(files, short, num=10)

            newest = cur_database["newest"]

            for f in file_dict:
                if int(f["last_modified"]) > cur_database["newest"]:
                    newest = int(f["last_modified"])
                    name_split = f["name"].split("/000/")[1].split("/00000/")[0].split("/")
                    if len(name_split) > 1:
                        name = int(name_split[0] + name_split[1])
                    else:
                        name = int(name_split[0] + "000")

                    if name not in to_write:
                        to_write.append(name)

        new_database = {"newest":newest, "files":{}}
        for name in to_write:
            new_database["files"][name] = dsname

        if new_database["files"]:
            with open("{0}/new_files.json".format(os.getcwd()), "w") as fhout:
                json.dump(new_database, fhout, sort_keys = True, indent = 4, separators=(',',':'))

        return

if __name__=='__main__':

    args = json.loads(sys.argv[1])

    handle_main(args)
