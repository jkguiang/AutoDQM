from datetime import datetime
import ROOT

def get_ref_cands(refs):

    ref_cands = {}

    best_ref = None
    first_order = None

    best_lumi_ratio = None
    most_recent = None
    for run in refs:
        # Recency
        this_age = refs[run]["run_age"]["total"]
        if not most_recent:
            most_recent = this_age
        elif this_age < most_recent:
            most_recent = this_age
            first_order = run
        # Statistics
        if not refs[run]["trigs_cut"]: continue
        # Lumi ratio
        this_lumi_ratio = refs[run]["lumi_ratio"]
        if refs[run]["lumi_ratio_cut"]:
            if not best_lumi_ratio: pass
            elif abs(1 - this_lumi_ratio) < abs(1 - best_lumi_ratio) and refs[run]["run_age"]["days"] < 10:
                best_ref = run
                ref_cands[run] = dict({"order":2, "best":False}, **refs[run])
            best_lumi_ratio = this_lumi_ratio

    # Set first order ref
    ref_cands[first_order] = dict({"order":1, "best":False}, **refs[run])

    # Set best ref
    if not best_ref:
        ref_cands[first_order]["best"] = True
    else:
        ref_cands[best_ref]["best"] = True
    
    return ref_cands 

def get_wbm_data(data_run, this_run, wbm):

    wbm_data = dict.fromkeys(["lumi_ratio", "run_dur", "run_age", "run_trigs", "trigs_cut", "lumi_ratio_cut"])

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
    wbm_data["run_dur"] = (this_stop_dt - this_start_dt).total_seconds()

    # Calculate time diff between run starts
    delta_dt = data_start_dt - this_start_dt
    # Difference in start times in [days, hours, minutes, total(in seconds)]
    wbm_data["run_age"] = {"days": delta_dt.days,
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
