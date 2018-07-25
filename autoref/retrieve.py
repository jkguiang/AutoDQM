# Imports
import json

# Run Registry API
from rhapi import DEFAULT_URL, RhApi

def retrieve(name, start_run=294927, folder="runreg_csc", table="datasets"):
    
    api = RhApi(DEFAULT_URL, debug = False)

    # Get column names and name of run column
    col_table = api.table(folder=folder, table=table)["columns"]
    print(col_table)
    cols=[]
    r_num = ""
    r_num_i = 0
    r_num_names = ["runnumber", "run_number"]
    for col in col_table:
        col_name = str(col["name"])
        cols.append(col_name)
        if not r_num:
            if col_name.lower() in r_num_names:
                r_num = col_name
                r_num_i = cols.index(col_name)
            if not r_num:
                for r_name in r_num_names:
                    if r_name in col_name.lower():
                        r_num = col_name
                        r_num_i = cols.index(col_name)
    if not r_num:
        r_num = cols[0]
    
    q = "select * from {0}.{1} r where r.{2}>:minrun".format(folder, table, r_num)
    print("Query: {}".format(q))
    p = {"minrun": start_run}
    qid = api.qid(q)


    data = {}
    it = 0
    all_runs = []
    while True:
        new_runs = 0
        runs = []
        raw_data = api.json(q, p)["data"]
        print("Iteration {0}: found {1} runs".format(it, len(raw_data)))
        for i in range(0, len(raw_data)):
            run = raw_data[i][r_num_i]
            runs.append(run)
            if run not in data:
                new_runs += 1
                all_runs.append(run)
            data[run] = {}
            for j in range(0, len(raw_data[i])):
                if j == r_num_i: continue
                data[run][cols[j]] = raw_data[i][j]
        if len(raw_data) < 1 or max(runs) == p["minrun"]:
            break
        p["minrun"] = max(runs) 
        it += 1
        print("Found {0} unique runs.".format(new_runs))

    file_map = {"data":data, "runs":all_runs}
    if data:
#        with open("{0}.json".format(name), "w") as fout:
#            print("Found {0} runs from {1}.{2}".format(len(data), folder, table))
#            json.dump(file_map, fout, indent=4)
#            print("Wrote data to {0}.json".format(name))
        return file_map
    else:
        print("Retrieval failed.")
        return None


if __name__ == "__main__":
    retrieve("data")
    retrieve("lumi", table="runs")
    #retrieve("lumi", folder="wbm", table="runs")
    #import test_smartref
    #test_smartref.main()
