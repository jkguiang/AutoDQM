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

    if str(data_run) not in dqm: return {}

    # Fetch WBM data
    if not os.path.isfile("{}/autoref/wbm.json".format(os.getcwd())):
        wbm = _fetch_sql_data("wbm", folder="runreg_csc", table="runs", save=True)
    else:
        with open("{}/autoref/wbm.json".format(os.getcwd()), "r") as fin:
            wbm = json.load(fin)

    if str(data_run) not in wbm: return {}

    ref_runs.sort()

    run_scan = range(0, ref_runs.index(data_run))
    run_scan.reverse()

    refs = {}
    best_ref = None
    best_ratio = None
    runback = 0 
    in_runreg = False
    for run_i in run_scan:
        this_run = ref_runs[run_i]
        # Skip runs missing from database
        if int(this_run) == int(data_run): continue
        if str(this_run) not in dqm: continue
        if str(this_run) not in wbm: continue
        in_runreg = True
        # Allow for max of 150 runs previous
        if runback > 150: break
        # Only runs marked as GOOD are approved for reference
        if dqm[str(this_run)]["RDA_CMP_OCCUPANCY"] != "GOOD": continue
        # Get available data from wbm.json
        lumi_ratio, run_dur_ratio, Nevents, delta_t = _get_wbm_data(data_run, this_run, wbm)
        # Zeroth order: High enough stats
        if Nevents and Nevents < 100000: continue
        passed_dur_cut = _get_ratio_cut(run_dur_ratio, cut=0.32)
        if not passed_dur_cut: continue
        # First order: recency
        if not best_ref:
            best_ref = this_run
            if lumi_ratio:
                best_ratio = lumi_ratio
                lumi_ratio = round(lumi_ratio, 3)
            else:
                lumi_ratio = "Not available"
            refs[this_run] = {"lumi_ratio":lumi_ratio, "Nevents":Nevents, "delta_t":delta_t, "order":1, "best":False}

        # Second order: luminocity
        else:
            passed_lumi_cut = _get_ratio_cut(lumi_ratio, best_ratio=best_ratio)
            if not passed_lumi_cut: continue
            elif int(delta_t["days"]) < 10:
                best_ref = this_run
                best_ratio = lumi_ratio
                refs[this_run] = {"lumi_ratio":round(lumi_ratio, 3), "Nevents":Nevents, "delta_t":delta_t, "order":2, "best":False}

        runback += 1

    if in_runreg:
        refs[best_ref]["best"] = True
        return refs
    else:
        return None

def _get_ratio_cut(ratio, best_ratio=None, cut=0.15):
    
    # Reset cut if not usable
    if cut < 0 or cut > 1: cut = 0.15

    passed_cut = False

    if not ratio: return passed_cut 

    abs_ratio = abs(ratio - 1)

    if abs_ratio < (cut): 
        if best_ratio and abs_ratio < abs(best_ratio - 1):
            passed_cut = True
        else:
            passed_cut = True

    return passed_cut


def _get_wbm_data(data_run, this_run, wbm):

    # Get approximate gauge of available statistics
    Ntriggers = wbm[str(this_run)]["TRIGGERS"]
    Nevents = (0.0028725994131)*Ntriggers+128324.464261 # from numpy fit done on uaf

    # Get run start and stop times
    data_start = wbm[str(data_run)]["STARTTIME"]
    data_stop = wbm[str(data_run)]["STOPTIME"]
    this_start = wbm[str(this_run)]["STARTTIME"]
    this_stop = wbm[str(this_run)]["STOPTIME"]

    data_start_dt = datetime.strptime(data_start, "%Y-%m-%d %H:%M:%S")
    data_stop_dt = datetime.strptime(data_stop, "%Y-%m-%d %H:%M:%S")
    this_start_dt = datetime.strptime(this_start, "%Y-%m-%d %H:%M:%S")
    this_stop_dt = datetime.strptime(this_stop, "%Y-%m-%d %H:%M:%S")

    # Calculate run duration
    data_run_dur = (data_start_dt - data_stop_dt)
    this_run_dur = (this_start_dt - this_stop_dt)
    run_dur_ratio = (float(data_run_dur.total_seconds())/float(this_run_dur.total_seconds()))

    # Calculate time diff between run starts
    delta_dt = data_start_dt - this_start_dt
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

    return lumi_ratio, run_dur_ratio, Nevents, delta_t

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
