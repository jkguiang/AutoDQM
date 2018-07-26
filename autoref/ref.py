import os
from time import mktime
from datetime import datetime
import ROOT
import json

def fetch_ref(data_run, ref_runs):
    
    # Fetch DQM data
    if not os.path.isfile("{}/autoref/dqm.json".format(os.getcwd())):
        dqm = _fetch_sql_data("dqm", folder="runreg_csc", table="datasets", save=True)
    else:
        with open("{}/autoref/dqm.json".format(os.getcwd()), "r") as fin:
            dqm = json.load(fin)

    # Fetch WBM data
    if not os.path.isfile("{}/autoref/wbm.json".format(os.getcwd())):
        wbm = _fetch_sql_data("wbm", folder="runreg_csc", table="runs", save=True)
    else:
        with open("{}/autoref/wbm.json".format(os.getcwd()), "r") as fin:
            wbm = json.load(fin)

    ref_runs.sort()

    run_scan = range(0, ref_runs.index(data_run))
    run_scan.reverse()

    refs = {}
    best_ref = None
    best_ratio = None
    break_counter = 0 
    in_runreg = False
    for run_i in run_scan:
        this_run = ref_runs[run_i]
        if int(this_run) == int(data_run): continue
        if str(this_run) not in dqm: continue
        in_runreg = True
        if break_counter > 100: break
        # Get available data from wbm.json
        lumi_ratio, Nevents, delta_t = _get_wbm_data(data_run, this_run, wbm)
        # Zeroth order: High enough stats
        if Nevents and Nevents < 100000: continue
        # First order: recency
        if not best_ref:
            if dqm[str(this_run)]["RDA_CMP_OCCUPANCY"] == "GOOD":
                best_ref = this_run
                if lumi_ratio: best_ratio = lumi_ratio
                refs[this_run] = {"lumi_ratio":lumi_ratio, "Nevents":Nevents, "delta_t":delta_t, "order":1, "best":False}
        # Second order: luminocity
        else:
            if dqm[str(this_run)]["RDA_CMP_OCCUPANCY"] != "GOOD": continue
            else:
                if not lumi_ratio: continue
                if lumi_ratio > 0.68 and lumi_ratio < 1.32:
                    if best_ratio:
                        if lumi_ratio > best_ratio and lumi_ratio < 1:
                            best_ref = this_run
                            best_ratio = lumi_ratio
                            refs[str(this_run)] = {"lumi_ratio":lumi_ratio, "Nevents":Nevents, "delta_t":delta_t, "order":2, "best":False}
                        elif lumi_ratio > 1 and lumi_ratio < best_ratio:
                            best_ref = this_run
                            best_ratio = lumi_ratio
                            refs[str(this_run)] = {"lumi_ratio":lumi_ratio, "Nevents":Nevents, "delta_t":delta_t, "order":2, "best":False}
                    else:
                        best_ref = this_run
                        best_ratio = lumi_ratio
                        refs[str(this_run)] = {"lumi_ratio":lumi_ratio, "Nevents":Nevents, "delta_t":delta_t, "order":2, "best":False}

        break_counter += 1

    if in_runreg:
        refs[best_ref]["best"] = True
        return refs
    else:
        return None

def _get_wbm_data(data_run, this_run, wbm):

    # Veto runs missing from WBM database
    if str(data_run) not in wbm: return None, None
    elif str(this_run) not in wbm: return None, None

    # Get approximate gauge of available statistics
    Ntriggers = wbm[str(this_run)]["TRIGGERS"]
    Nevents = (0.0028725994131)*Ntriggers+128324.464261 # from numpy fit done on uaf

    # Get run start time, time between runs
    data_start = wbm[str(data_run)]["STARTTIME"]
    this_start = wbm[str(this_run)]["STARTTIME"]

    data_dt = datetime.strptime(data_start, "%Y-%m-%d %H:%M:%S")
    this_dt = datetime.strptime(this_start, "%Y-%m-%d %H:%M:%S")

    delta_dt = data_dt - this_dt
    # Difference in start times in [days, hours, minutes, total(in seconds)]
    delta_t = {"days": delta_dt.days,
               "hours": delta_dt.seconds//3600,
               "minutes": (delta_dt.seconds//60)%60,
               "total": delta_dt.total_seconds()}

    # Get luminosity ratio
    try:
        data_init_lumi = float(wbm[str(data_run)]["INITLUMI"])
        data_end_lumi = float(wbm[str(data_run)]["ENDLUMI"])
        data_avg_lumi = _get_avg_lumi(data_init_lumi, data_end_lumi)
        this_init_lumi = float(wbm[str(this_run)]["INITLUMI"])
        this_end_lumi = float(wbm[str(this_run)]["ENDLUMI"])
        this_avg_lumi = _get_avg_lumi(this_init_lumi, this_end_lumi)
    except TypeError: 
        data_avg_lumi = 0
        this_avg_lumi = 0

    if this_avg_lumi > 0:
        lumi_ratio = data_avg_lumi/this_avg_lumi
    else:
        lumi_ratio = None

    return lumi_ratio, Nevents, delta_t

def _get_avg_lumi(init_lumi, end_lumi):

    if init_lumi*end_lumi == 0: return 0
    if not init_lumi or not end_lumi: return 0

    diff = init_lumi-end_lumi
    quot = init_lumi/end_lumi

    avg = diff/ROOT.TMath.Log(quot)

    return avg

def _fetch_sql_data(name, start_run=294927, folder="runreg_csc", table="datasets", save=False):

    # Run Registry API
    from rhapi import DEFAULT_URL, RhApi
    
    api = RhApi(DEFAULT_URL, debug = False)

    # Get column names and name of run column
    col_table = api.table(folder=folder, table=table)["columns"]
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
    
    q = "select * from {0}.{1} r where r.{2}>:minrun order by r.{2}".format(folder, table, r_num)
    p = {"minrun": start_run}
    qid = api.qid(q)

    data = {}
    it = 0
    while True:
        new_runs = 0
        runs = []
        raw_data = api.json(q, p)["data"]
        for i in range(0, len(raw_data)):
            run = raw_data[i][r_num_i]
            runs.append(run)
            if run not in data:
                new_runs += 1
            if run not in data: data[run] = {}
            for j in range(0, len(raw_data[i])):
                if j == r_num_i: continue
                if cols[j] == "RDA_NAME":
                    if "Express" not in raw_data[i][j]: continue
                    if "PromptReco" not in raw_data[i][j]: continue
                data[run][cols[j]] = raw_data[i][j]
            if not data[run]: del data[run]
        if len(raw_data) < 1 or max(runs) == p["minrun"]:
            break
        p["minrun"]+=500 
        it += 1

    if data and save: 
        with open("{0}/autoref/{1}.json".format(os.getcwd(), name), "w") as fout:
            json.dump(data, fout, indent=4)
        return data
    else:
        return None

if __name__ == "__main__":
    pass
