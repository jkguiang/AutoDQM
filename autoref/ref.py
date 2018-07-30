import os
from time import mktime
from datetime import datetime
import ROOT
import json

import sql

def fetch_ref(data_run, ref_runs):

    if type(data_run) != int:
        data_run = int(data_run)

    dqm = {}
    wbm = {}
    folder = "runreg_csc"

    ref_runs.sort()
    run_scan = range(0, ref_runs.index(str(data_run)))
    run_scan.reverse()
    runback = run_scan[0:156]

    dqm = sql.fetch(max_run=data_run, min_run=int(ref_runs[runback[-1]]), folder=folder, table="datasets")
    if data_run not in dqm:
        return {}
    wbm = sql.fetch(max_run=data_run, min_run=int(ref_runs[runback[-1]]), folder=folder, table="runs")
    if data_run not in wbm:
        return {}

    refs = {}
    best_ref = None
    best_ratio = None
    in_runreg = False

    for run_i in runback:

        this_run = int(ref_runs[run_i])
        if this_run == data_run: continue
        if len(refs) == 3:
            refs[best_ref]["best"] = True
            return refs

        # Skip runs missing from database
        if this_run not in dqm or this_run not in wbm: continue
        in_runreg = True

        # Only runs marked as GOOD are approved for reference
        if dqm[this_run]["RDA_CMP_OCCUPANCY"] != "GOOD": continue

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

        # Second order: luminosity
        else:
            passed_lumi_cut = _get_ratio_cut(lumi_ratio, best_ratio=best_ratio)
            if not passed_lumi_cut: continue
            elif int(delta_t["days"]) < 10:
                best_ref = this_run
                best_ratio = lumi_ratio
                refs[this_run] = {"lumi_ratio":round(lumi_ratio, 3), "Nevents":Nevents, "delta_t":delta_t, "order":2, "best":False}

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
    Ntriggers = wbm[this_run]["TRIGGERS"]
    Nevents = (0.0028725994131)*Ntriggers+128324.464261 # from numpy fit done on uaf

    # Get run start and stop times
    data_start = wbm[data_run]["STARTTIME"]
    data_stop = wbm[data_run]["STOPTIME"]
    this_start = wbm[this_run]["STARTTIME"]
    this_stop = wbm[this_run]["STOPTIME"]

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
        data_init_lumi = float(wbm[data_run]["INITLUMI"])
        data_end_lumi = float(wbm[data_run]["ENDLUMI"])
        data_avg_lumi = _get_avg_lumi(data_init_lumi, data_end_lumi)
        this_init_lumi = float(wbm[this_run]["INITLUMI"])
        this_end_lumi = float(wbm[this_run]["ENDLUMI"])
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

if __name__ == "__main__":
    pass
