# Imports
import json

# Run Registry API
from rhapi import DEFAULT_URL, RhApi

def fetch(max_run=320008, min_run=316766, folder="runreg_csc", table="datasets"):

    api = RhApi(DEFAULT_URL, debug = False)

    # Get column names and name of run column
    col_table = api.table(folder=folder, table=table)["columns"]
    cols=[]
    r_num = ""
    r_num_i = 0
    for col in col_table:
        col_name = str(col["name"])
        if _get_data_col(col_name, table): cols.append(col_name)
        if not r_num and _get_run_col(col_name):
            cols.append(col_name)
            r_num = col_name
            r_num_i = cols.index(col_name)

    if not r_num:
        r_num = cols[0]
    
    # Form query
    c = ",".join("r."+x for x in cols)
    q = "select {0} from {1}.{2} r where r.{3}>=:minrun and r.{3}<=:maxrun order by r.{3}".format(c, folder, table, r_num)
    p = {"maxrun":max_run, "minrun":min_run}
    qid = api.qid(q)

    data = {}
    it = 0
    while True:
        runs = []
        raw_data = api.json(q, p)["data"]

        for i in range(0, len(raw_data)):

            run = raw_data[i][r_num_i]
            runs.append(run)

            if run not in data:
                data[run] = {}
            for j in range(0, len(raw_data[i])):
                if j == r_num_i: continue
                if cols[j] == "RDA_NAME":
                    # Filter for Express and PromptReco data
                    if "Express" not in raw_data[i][j]: continue
                    if "PromptReco" not in raw_data[i][j]: continue
                data[run][cols[j]] = raw_data[i][j]
            if not data[run]: del data[run]

        if len(raw_data) < 1 or max(runs) == p["minrun"] or p["minrun"] >= p["maxrun"]:
            break
        p["minrun"]=max(runs) 
        it += 1

    if data:
        return data 
    else:
        return None

def _get_data_col(col_name, table):
    if table == "datasets":
        return "RDA_CMP" in col_name and "COMMENT" not in col_name and "CAUSE" not in col_name
    if table == "runs":
        return "TRIGGERS" in col_name or "LUMI" in col_name or "TIME" in col_name

def _get_run_col(col_name):
    r_num_names = ["runnumber", "run_number"]
    if col_name.lower() in r_num_names:
        return True 
    else:
        for r_name in r_num_names:
            if r_name in col_name.lower():
                return True
    return False

if __name__ == "__main__":
    pass
