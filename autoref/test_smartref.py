import json

def main():
    data = {}
    lumi = {}

    with open("data.json", "r") as fin:
        data = json.load(fin)

    with open("lumi.json", "r") as fin:
        lumi = json.load(fin)

    data_collis_count = 0
    data_cosmic_count = 0
    data_total = len(data)
    data_runs = []

    for run in data:
        data_run_type = data[run]["RDA_NAME"]
        if "collision" in data_run_type.lower(): data_collis_count += 1
        if "cosmic" in data_run_type.lower(): data_cosmic_count += 1

    lumi_collis_count = 0
    lumi_cosmic_count = 0
    lumi_total = len(lumi)
    lumi_runs = []

    for run in lumi:
        lumi_run_type = lumi[run]["TRIGGERMODE"]
        if "collision" in lumi_run_type.lower(): lumi_collis_count += 1
        if "cosmic" in lumi_run_type.lower(): lumi_cosmic_count += 1

    matched_collis = 0
    matched_cosmic = 0
    matched_total = 0

    for run in data:
        if run in lumi:
            matched_total += 1
            data_run_type = data[run]["RDA_NAME"]
            lumi_run_type = lumi[run]["TRIGGERMODE"]
            if "collision" in data_run_type.lower() and "collision" in lumi_run_type.lower():
                matched_collis += 1
            if "cosmic" in data[run]["RDA_NAME"].lower() and "cosmic" in lumi_run_type.lower():
                matched_cosmic += 1

    print("{0}/{1} data runs matched ({0}/{2} lumi runs)".format(matched_total, data_total, lumi_total))
    print("{0}/{1} data collision runs matched ({0}/{2} lumi)".format(matched_collis, data_collis_count, lumi_collis_count))
    print("{0}/{1} data cosmic runs matched ({0}/{2} lumi)".format(matched_cosmic, data_cosmic_count, lumi_cosmic_count))

def run_density():

    data = {}
    lumi = {}

    with open("data.json", "r") as fin:
        data = json.load(fin)

    with open("lumi.json", "r") as fin:
        lumi = json.load(fin)

    data_runs = []
    lumi_runs = []

    for run in data:
        data_runs.append(run)
    for run in lumi:
        lumi_runs.append(run)
    
    data_total = len(data_runs)
    lumi_total = len(lumi_runs)

    print("Data: max run -> {0}, min run -> {1} ({2} run density)".format(max(data_runs), min(data_runs), data_total/(float(max(data_runs))-float(min(data_runs)))))
    print("Lumi: max run -> {0}, min run -> {1} ({2} run density)".format(max(lumi_runs), min(lumi_runs), lumi_total/(float(max(lumi_runs))-float(min(lumi_runs)))))

    print("Comparing good runs:")
    good_data_count = 0
    good_data_match = 0
    rereco_count = 0
    rereco_match = 0
    for run in data:
        if data[run]["RDA_CMP_OCCUPANCY"] == "GOOD":
            good_data_count += 1
            if run in lumi:
                good_data_match += 1
            if "ReReco" in data[run]["RDA_NAME"]:
                rereco_count += 1
                if run in lumi:
                    rereco_match += 1

    print("{0}/{1} good runs matched".format(good_data_match, good_data_count))
    print("{0}/{1} good, ReReco runs matched".format(rereco_match, rereco_count))


    return

if __name__ == "__main__":
    run_density()
