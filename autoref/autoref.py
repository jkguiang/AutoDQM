import os
import json

import retrieve
import get_runs

def autoref(data_run):
    
    if not os.path.isfile("dqm.json"):
        dqm_map = retrieve.retrieve("dqm", save=True)
    else:
        with open("dqm.json", "r") as fin:
            dqm_map = json.load(fin)
    if not os.path.isfile("lumi.json"):
        lumi_map = retrieve.retrieve("lumi", table="runs", save=True)
    else:
        with open("lumi.json", "r") as fin:
            lumi_map = json.load(fin)

    dqm_runs = dqm_map["runs"]
    dqm = dqm_map["data"]
    lumi = lumi_map["data"]

    ref_runs = get_runs.main("Run2018_Cosmics.txt")
    ref_runs.sort()

    run_scan = range(0, ref_runs.index(data_run))
    run_scan.reverse()

    O1_ref = {} 
    O2_refs = {} 
    best_ref = None
    best_ratio = None
    break_counter = 0 
    in_runreg = False
    for run_i in run_scan:
        this_run = ref_runs[run_i]
        if int(this_run) == int(data_run): continue
        if this_run not in dqm_runs: continue
        in_runreg = True
        if break_counter > 100: break
        # First order: recency
        if not best_ref:
            if dqm[str(this_run)]["RDA_CMP_OCCUPANCY"] == "GOOD":
                best_ref = this_run
                lumi_ratio = get_lumi_ratio(data_run, this_run, lumi) 
                if lumi_ratio: best_ratio = lumi_ratio
                O1_ref[this_run] = lumi_ratio
        # Second order: luminocity
        else:
            if dqm[str(this_run)]["RDA_CMP_OCCUPANCY"] != "GOOD": continue
            else:
                lumi_ratio = get_lumi_ratio(data_run, this_run, lumi)
                if not lumi_ratio: continue
                if lumi_ratio > 0.68 and lumi_ratio < 1.32:
                    if best_ratio:
                        if lumi_ratio > best_ratio and lumi_ratio < 1:
                            best_ref = this_run
                            best_ratio = lumi_ratio
                            O2_refs[str(this_run)] = lumi_ratio
                        elif lumi_ratio > 1 and lumi_ratio < best_ratio:
                            best_ref = this_run
                            best_ratio = lumi_ratio
                            O2_refs[str(this_run)] = lumi_ratio
                    else:
                        best_ref = this_run
                        best_ratio = lumi_ratio
                        O2_refs[str(this_run)] = lumi_ratio

        break_counter += 1

    if in_runreg:
        print("------------------ DATA: {0} ------------------".format(data_run))
        print("Best ref: {0}".format(best_ref))
        print("First order ref: {0}".format(O1_ref))
        if O2_refs:
            print("Second order refs: {0}".format(O2_refs))
    else:
        print("No ref found")

    return

def get_lumi_ratio(data_run, this_run, lumi):

    if str(data_run) not in lumi: return None
    elif str(this_run) not in lumi: return None

    try:
        data_avg_lumi = (float(lumi[str(data_run)]["INITLUMI"])+float(lumi[str(data_run)]["ENDLUMI"]))/2
        if data_avg_lumi == 0: return None
        this_avg_lumi = (float(lumi[str(this_run)]["INITLUMI"])+float(lumi[str(this_run)]["ENDLUMI"]))/2
        if this_avg_lumi == 0: return None
    except TypeError: 
        return None

    lumi_ratio = data_avg_lumi/this_avg_lumi

    return lumi_ratio


if __name__ == "__main__":
    runs = get_runs.main("Run2018_Cosmics.txt")
    #import random
    #data_run = (runs[random.randint(0,len(runs)-1)])
    for data_run in runs:
        autoref(data_run)
