import os
import json
import retrieve

def autoref(data_run):
    
    if not os.path.isfile("data.json"):
        data_map = retrieve.retrieve("data")
    else:
        with open("data.json", "r") as fin:
            data_map = json.load(fin)
    if not os.path.isfile("lumi.json"):
        lumi_map = retrieve.retrieve("lumi", table="runs")
    else:
        with open("lumi.json", "r") as fin:
            lumi_map = json.load(fin)

    data_runs = data_map["runs"]
    data = data_map["data"]
    lumi = lumi_map["data"]
    if int(data_run) not in data_runs:
        print("Data run not in runreg_csc.datasets")
        return
    data_runs.sort()

    run_scan = range(0, data_runs.index(data_run))
    run_scan.reverse()

    O1_ref = {} 
    O2_refs = {} 
    best_ref = None
    best_ratio = None
    break_counter = 0 
    for run_i in run_scan:
        if break_counter > 100: break
        this_run = data_runs[run_i]
        # First order: recency
        if not best_ref:
            if data[str(this_run)]["RDA_CMP_OCCUPANCY"] == "GOOD":
                best_ref = this_run
                lumi_ratio = get_lumi_ratio(data_run, this_run, lumi) 
                if lumi_ratio: best_ratio = lumi_ratio
                O1_ref[this_run] = lumi_ratio
        # Second order: luminocity
        else:
            if data[str(this_run)]["RDA_CMP_OCCUPANCY"] != "GOOD": continue
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

    print("------------------ DATA: {0} ------------------".format(data_run))
    print("Best ref: {0}".format(best_ref))
    print("First order ref: {0}".format(O1_ref))
    print("Second order refs: {0}".format(O2_refs))

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
    autoref(312001)
