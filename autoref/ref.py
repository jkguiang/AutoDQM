import os
from datetime import datetime
import ROOT


def get_best(refs):

    # Best ref to override 1st order ref
    best_ref = None

    # Parse over refs and
    best_lumi_ratio = None
    for run in refs:
        # Lumi ratio
        this_lumi_ratio = refs[run]["lumi_ratio"]
        if not best_lumi_ratio or abs(1 - this_lumi_ratio) < abs(1 - best_lumi_ratio):
            best_lumi_ratio = this_lumi_ratio
            best_ref = run

    return best_ref

def get_wbm_data(data_run, this_run, wbm):

    wbm_data = dict.fromkeys(["lumi_ratio", "this_run_dur", "delta_t", "run_trigs", "trigs_cut", "lumi_ratio_cut"])

    # Get run triggers
    this_run_trigs = wbm[this_run]["TRIGGERS"]
    wbm_data["trigs_cut"] = int(this_run_trigs) > 8*10**7 

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
    wbm_data["this_run_dur"] = (this_stop_dt - this_start_dt).total_seconds()

    # Calculate time diff between run starts
    delta_dt = data_start_dt - this_start_dt
    # Difference in start times in [days, hours, minutes, total(in seconds)]
    wbm_data["delta_t"] = {"days": delta_dt.days,
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
        wbm_data["lumi_ratio"] = data_avg_lumi/this_avg_lumi
        wbm_data["lumi_ratio_cut"] = abs(1 - wbm_data["lumi_ratio"]) < 0.15

    return wbm_data 

def _get_avg_lumi(init_lumi, end_lumi):

    if init_lumi*end_lumi == 0: return 0
    if not init_lumi or not end_lumi: return 0

    diff = init_lumi-end_lumi
    quot = init_lumi/end_lumi

    avg = diff/ROOT.TMath.Log(quot)

    return avg

if __name__ == "__main__":
    pass
