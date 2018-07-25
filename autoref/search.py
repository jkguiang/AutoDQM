import json
import pprint

data = {}
lumi = {}
with open("data.json", "r") as fin:
    data = json.load(fin)["data"]
with open("lumi.json", "r") as fin:
    lumi = json.load(fin)["data"]

def search(run=None, toggle_print=False):
    if not run: return

    global data
    global lumi

    found = False
    found_data = False
    found_lumi = False

    if run in data:
        found_data = True
        found = True
    if run in lumi:
        found_lumi = True
        found = True

    if not found:
        if toggle_print: print("{0} is not in either JSON".format(run))
    if found_data and found_lumi:
        if toggle_print: print("-> Found {0} in both data and lumi! <-".format(run))
    else:
        if found_data:
            if toggle_print: print("Found {0} in data.json".format(run))
        if found_lumi:
            if toggle_print: print("Found {0} in lumi.json".format(run))
    
    return found_data, found_lumi, found
    
def find_bad():
    global data
    global lumi

    total = len(data)
    bad_count = 0
    for run in data:
        if data[run]["RDA_CMP_OCCUPANCY"] == "BAD":
            bad_count += 1
            print("Bad run {0} in {1}".format(run, data[run]["RUN_CLASS_NAME"]))
            if run in lumi:
                print("Bad run {0} is in data and lumi".format(run))
    print("{0}/{1} data runs are marked as bad".format(bad_count, total))

def one_by_one():
    while True:
        run = raw_input("Run Number: ")
        if run == "quit" or run == ".q": break
        elif run.isdigit():
            search(run, toggle_print=True)
        else:
            print("enter 'quit' or '.q' to exit.")

def from_file(runs_file):
    import get_runs
    runs = get_runs.main(runs_file)
    data_count = 0
    lumi_count = 0
    both_count = 0
    for run in runs:
        found_data, found_lumi, found = search(str(run), toggle_print=True)
        if found_data: data_count += 1
        if found_lumi: lumi_count += 1
        if found_data and found_lumi: both_count += 1

    print("-----------------RESULTS-----------------")
    print("Results for {0}:".format(runs_file))
    print("{0}/{1} runs in data ({2}%)".format(data_count, len(runs), float(data_count)/len(runs)*100))
    print("{0}/{1} runs in lumi ({2}%)".format(lumi_count, len(runs), float(lumi_count)/len(runs)*100))
    print("{0}/{1} runs in both ({2}%)".format(both_count, len(runs), float(both_count)/len(runs)*100))


if __name__ == "__main__":
    #from_file("Run2017_SingleMuon.txt")
    #from_file("Run2018_SingleMuon.txt")
    #from_file("Run2018_Cosmics.txt")
    find_bad()
