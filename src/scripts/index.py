import os
import sys
import json
import time
import ROOT
import subprocess
import traceback


import fetch
import search
import AutoDQM
from HistPair import HistPair

# Global dict for holding all run times
times = {}
cur_dir = os.getcwd()

# Path to root directory
main_dir = os.path.dirname(os.path.dirname(os.getcwd()))

# Recursively find unique name for function call
def get_name(name, counter):
    new_name = name + str(counter)
    if new_name in times:
        counter += 1
        return get_name(name, counter)
    else:
        return (new_name)

# Wrapper for timing functions
def timer(func):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)

        times[get_name(func.__name__, 0)] = (time.time() - t0)
        return result
    return wrapper

def get_response(t0, status, fail_reason, tb, query, payload):
    duration = time.time() - t0
    return json.dumps( { "query": query, "start": t0, "duration":duration, "response": { "status": status, "fail_reason": str(fail_reason), "traceback": str(tb), "payload": times } } )


@timer
def compile_hists(subsystem, data_fname, ref_fname, data_run, ref_run):
    # Load config
    with open("{0}/data/configs.json".format(main_dir)) as config_file:
        config = json.load(config_file)
    conf_list = config[subsystem]["hists"]
    main_gdir = config[subsystem]["main_gdir"]

    data_file = ROOT.TFile.Open(data_fname)
    ref_file = ROOT.TFile.Open(ref_fname)
    histPairs = []

    for hconf in conf_list:
        # Get name of hist in root file
        h = str(hconf["path"].split("/")[-1])
        # Get parent directory of hist
        gdir = str(hconf["path"].split(h)[0])

        # Get keys of directory (for wildcard)
        data_dir = data_file.GetDirectory(
                "{0}{1}".format(main_gdir.format(data_run), gdir))
        ref_dir = ref_file.GetDirectory(
                "{0}{1}".format(main_gdir.format(ref_run), gdir))

        data_keys = data_dir.GetListOfKeys()
        ref_keys = ref_dir.GetListOfKeys()

        # Wildcard search
        if "*" in h:
            # Check entire directory for files matching wildcard
            count = 0
            for name in [key.GetName() for key in data_keys]:
                if h.split("*")[0] in name and ref_keys.Contains(name):
                    data_hist = data_dir.Get(name)
                    ref_hist = ref_dir.Get(name)
                    data_hist.SetDirectory(0)
                    ref_hist.SetDirectory(0)
                    hPair = HistPair(data_hist, ref_hist, hconf)
                    # Add an index if there will be multiple hists with the same name_out
                    if "name_out" in hconf: hPair.name_out += "_{0}".format(count)
                    histPairs.append(hPair)
                    count += 1
        # Normal search
        else:
            if data_keys.Contains(h) and ref_keys.Contains(h):
                data_hist = data_dir.Get(h)
                ref_hist = ref_dir.Get(h)
                data_hist.SetDirectory(0)
                ref_hist.SetDirectory(0)
                hPair = HistPair(data_hist, ref_hist, hconf)
                histPairs.append(hPair)
    

    data_file.Close()
    ref_file.Close()
    return histPairs

def check(is_success, fail_reason):
    if not is_success: raise Exception('Error: {0}'.format(fail_reason))
    else: return None

@timer
def get_hists(subsystem, db_dir, data_id, ref_id, user_id):
    data_fname = "{0}/{1}.root".format(db_dir, data_id)
    ref_fname = "{0}/{1}.root".format(db_dir, ref_id)
    histPairs = compile_hists(subsystem, data_fname, ref_fname, data_id, ref_id)

    subprocess.check_call(["{0}/make_html.sh".format(cur_dir), "setup", user_id])

    AutoDQM.autodqm(histPairs, data_id, ref_id, user_id)

    subprocess.check_call(["{0}/make_html.sh".format(cur_dir), "updt", user_id])

    return True, None

def handle_args(args):

    # Values for tracking script's progress
    is_success = False
    fail_reason = None

    try:
        if args["type"] == "retrieve_data":
            is_success, fail_reason = fetch.fetch(args["series"], args["sample"], args["data_info"])
            check(is_success, fail_reason)
        elif args["type"] == "retrieve_ref":
            is_success, fail_reason = fetch.fetch(args["series"], args["sample"], args["ref_info"])
            check(is_success, fail_reason)

        elif args["type"] == "process":
            is_success, fail_reason = get_hists(args["subsystem"], "{0}/data/database/{1}/{2}".format(main_dir, args["series"], args["sample"]), args["data_info"], args["ref_info"], args["user_id"])
            check(is_success, 'get_hists')

    except Exception as error:
        fail_reason = str(error)
        return is_success, fail_reason, traceback.format_exc()

    return is_success, fail_reason, None

def process_query(args):
    t0 = time.time()

    is_success, fail_reason, tb = handle_args(args)
    
    if is_success and fail_reason == None:
        return get_response(t0, "success", fail_reason, tb, args,  "Query proccessed successfully")
    else:
        return get_response(t0, "fail", fail_reason, tb, args,  "Query failed")

if __name__ == "__main__":
    # print(process_query(["0th_index_is__this_file.py","/RelValZMM_14/CMSSW_9_1_1_patch1-PU25ns_91X_upgrade2023_realistic_v3_D17PU140-v1/DQMIO", "/RelValZMM_14/CMSSW_9_3_0_pre3-PU25ns_92X_upgrade2023_realistic_v2_D17PU140-v2/DQMIO", "RelVal", "ZMM_14", "ZMM_14"]))
    # print process_query(["0th_indix_is_this_file.py", "SingleMuon", "300811", "/SingleMuon/Run2017C-PromptReco-v3/DQMIO", "301531", "/SingleMuon/Run2017C-PromptReco-v3/DQMIO"])
    # test = {"type":"retrieve_data","sample":"SingleMuon", "ref_info":"307063", "data_info":"307082", "user_id":str(1519083858797)}
    # print(process_query(test))
    # test2 = {"type":"retrieve_ref","sample":"SingleMuon", "ref_info":"307063", "data_info":"307082", "user_id":str(1519083858797)}
    # print(process_query(test2))
    # test3 = {"type":"process","sample":"SingleMuon", "ref_info":"307063", "data_info":"307082", "user_id":str(1519083858797)}
    # print(process_query(test3))

    args = json.loads(sys.argv[1])
    print(process_query(args))

