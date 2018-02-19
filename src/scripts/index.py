import os
import sys
import json
import time
import ROOT
import subprocess

import fetch
import search
import AutoDQM

# Global dict for holding all run times
times = {}
cur_dir = os.getcwd()

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

def get_response(t0, status, fail_reason, query, payload):
    duration = time.time() - t0
    return json.dumps( { "query": query, "start": t0, "duration":duration, "response": { "status": status, "fail_reason": str(fail_reason), "payload": times } } )


@timer
def compile_hists(new_file):

    f = ROOT.TFile.Open(new_file)
    hists = {}

    h_list = ROOT.gDirectory.GetListOfKeys()

    for h in h_list:
        hists[h.GetName()] = h.ReadObj()
        hists[h.GetName()].SetDirectory(0)

    f.Close()

    return hists

def check(is_success, fail_reason):
    if not is_success: raise Exception('Error: {0}'.format(fail_reason))
    else: return None

@timer
def get_hists(fdir, rdir, data_id, ref_id, user_id):
    f_hists = compile_hists("{0}/{1}.root".format(fdir, data_id))
    r_hists = compile_hists("{0}/{1}.root".format(rdir, ref_id))

    subprocess.check_call(["{0}/make_html.sh".format(cur_dir), "setup", user_id])

    AutoDQM.autodqm(f_hists, r_hists, data_id, ref_id, user_id)

    subprocess.check_call(["{0}/make_html.sh".format(cur_dir), "updt", user_id])

    return True, None

def handle_args(args):

    # Values for tracking script's progress
    is_success = False
    fail_reason = None

    try:
        if args["type"] == "retrieve_data":
            is_success, fail_reason = fetch.fetch(args["data_info"], args["sample"], "{0}/data/{1}".format(os.path.abspath(os.pardir), args["user_id"]))
            check(is_success, fail_reason)
        elif args["type"] == "retrieve_ref":
            is_success, fail_reason = fetch.fetch(args["ref_info"], args["sample"], "{0}/ref/{1}".format(os.path.abspath(os.pardir), args["user_id"]))
            check(is_success, fail_reason)

        elif args["type"] == "process":
            # Root files should now be in data and ref directories
            is_success, fail_reason = get_hists(args["subys"], "{0}/data/{1}".format(os.path.abspath(os.pardir), args["user_id"]), "{0}/ref/{1}".format(os.path.abspath(os.pardir), args["user_id"]), args["data_info"], args["ref_info"], args["user_id"])
            check(is_success, 'get_hists')

    except Exception as error:
        fail_reason = str(error)
        return is_success, fail_reason

    return is_success, fail_reason

def process_query(args):
    t0 = time.time()

    samples = ["Cosmics", "SingleMuon"]

    if args["sample"] in samples:
        is_success, fail_reason = handle_args(args)
    else:
        return get_response(t0, "fail", "Sample not supported", args,  "Query failed")
    
    if is_success and fail_reason == None:
        return get_response(t0, "success", fail_reason, args,  "Query proccessed successfully")
    else:
        return get_response(t0, "fail", fail_reason, args,  "Query failed")

if __name__ == "__main__":
    # print(process_query(["0th_index_is__this_file.py","/RelValZMM_14/CMSSW_9_1_1_patch1-PU25ns_91X_upgrade2023_realistic_v3_D17PU140-v1/DQMIO", "/RelValZMM_14/CMSSW_9_3_0_pre3-PU25ns_92X_upgrade2023_realistic_v2_D17PU140-v2/DQMIO", "RelVal", "ZMM_14", "ZMM_14"]))
    # print process_query(["0th_indix_is_this_file.py", "SingleMuon", "300811", "/SingleMuon/Run2017C-PromptReco-v3/DQMIO", "301531", "/SingleMuon/Run2017C-PromptReco-v3/DQMIO"])
    # test = {"type":"retrieve_data","sample":"SingleMuon", "ref_info":"301531", "ref_query":"/SingleMuon/Run2017C-PromptReco-v3/DQMIO", "data_info":"301165", "data_query":"/SingleMuon/Run2017C-PromptReco-v1/DQMIO", "user_id":str(int(time.time()))}
    # print(process_query(test))

    args = json.loads(sys.argv[1])
    print(process_query(args))

