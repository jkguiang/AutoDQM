import os
import sys
import json
import time
import ROOT
import subprocess

import dis_client
import AutoDQM

# Global dict for holding all run times
times = {}

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
    warning = None
    return json.dumps( { "query": query, "start": t0, "duration":duration, "response": { "status": status, "fail_reason": fail_reason, "warning": warning, "payload": times } } )

@timer
def compile_hists(new_dir):
    old_h = {}
    dir_list = os.listdir(new_dir)
    counter = 0
    for path in dir_list:
        f = ROOT.TFile(new_dir + "/" + path)
        trees = {1:{"tree":f.Get("TH2Fs"), "type":ROOT.TH2F},
                2:{"tree":f.Get("TH1Fs"), "type":ROOT.TH1F, "hists":["hSnhits", "hSnSegments", "hWirenGroupsTotal", "hStripNFired", "hRHnrechits"], 
                                                            "wildcards":["hRHTimingAnode", "hRHTiming", "hWireTBin"]}}

        for t_dict in trees.values():

            for event in t_dict["tree"]:
                path = str(event.FullName)
                name = str(event.Value.GetName())

                # Only look at muon paths
                if not ("CSC/CSCOfflineMonitor" in path): continue
                if type(event.Value) != t_dict["type"]: continue
                # Special 1D Histogram Checks
                if type(event.Value) == ROOT.TH1F:
                    passed = False
                    if name in t_dict["hists"]: passed = True
                    if not passed:
                        for wc in t_dict["wildcards"]:
                            if wc in name:
                                passed = True
                    if not passed: continue


                if name not in old_h:
                    old_h[name] = event.Value.Clone(name)
                    old_h[name].SetDirectory(0)
                else:
                    old_h[name].Add(event.Value)

        f.Close()

    return old_h

@timer
def get_hists(fdir, rdir, f_id):
    f_hists = compile_hists(fdir)
    r_hists = compile_hists(rdir)

    subprocess.check_call(["{0}/make_html.sh".format(os.getcwd()), "setup"])

    # AutoDQM takes dicts of data and ref hists, 'ID' of sample (i.e. PU200, noPU, etc. May change this later), and target directory (currently using cwd)
    AutoDQM.autodqm(f_hists, r_hists, f_id, os.getcwd())

    subprocess.check_call(["{0}/make_html.sh".format(os.getcwd()), "updt"])

    return True

# Generates 'id' used to identify RelVal comparison plots
def get_id(path):
    return path.split("/DQMIO")[0].split("_")[-1].split("-")[0]

# Generates run number for SingleMuon identification
def get_run(path):
    split = path.split("/000/")[1].split("/00000/")[0].split("/")
    return (split[0] + split[1])

@timer
def get_files(path, targ_dir, run=None):

    response = dis_client.query(q=path, typ="files", detail=True)
    data = response["response"]["payload"]
    xrd_args = ["{0}/get_xrd.sh".format(os.getcwd()), targ_dir]

    # Path to targ dir, used to check if files already exist
    cur_dir = os.listdir(os.getcwd() + "/" +  targ_dir)

    for tfile in data:
        # Check if files already downloaded to targ_dir
        if tfile["name"].split("/")[-1] in cur_dir: return True
        if run:
            # keep this check separate from run existance check so file is not appended in else statement
            if run == get_run(tfile["name"]):
                xrd_args.append(tfile["name"])
        else:
            xrd_args.append(tfile["name"])

    if len(xrd_args) == 2: return False

    subprocess.check_call(xrd_args)
    return True

def check(is_success, func):
    if not is_success: raise Exception('Function failed: {0}'.format(func))
    else: return None

def handle_RelVal(args):
    
    # Ensure pile-up matches
    if (get_id(args[1]) != get_id(args[2])):
        return False 

    # Values for tracking script's progress
    is_success = False
    fail_reason = None

    try:
        # Generate root files via bash subprocess
        is_success = get_files(str(args[1]), "data")
        check(is_success, 'get_files')
        is_success = get_files(str(args[2]), "ref")
        check(is_success, 'get_files')

        # Root files should now be in data and ref directories
        is_success = get_hists("{0}/data".format(os.getcwd()), "{0}/ref".format(os.getcwd()), get_id(args[1]))
        check(is_success, 'get_hists')

    except Exception as error:
        fail_reason = error
        return is_success, fail_reason

    return is_success, fail_reason

def handle_SingleMuon(args):

    # Values for tracking script's progress
    is_success = False
    fail_reason = None

    try:
        # Generate root files via bash subprocess
        is_success = get_files(str(args[1]), "data", args[4])
        check(is_success, 'get_files')
        is_success = get_files(str(args[2]), "ref", args[4])
        check(is_success, 'get_files')

        # Root files should now be in data and ref directories
        is_success = get_hists("{0}/data".format(os.getcwd()), "{0}/ref".format(os.getcwd()), get_id(args[1]))
        check(is_success, 'get_hists')

    except Exception as error:
        fail_reason = error
        return is_success, fail_reason

    return is_success, fail_reason

def process_query(args):
    t0 = time.time()

    if args[3] == "RelVal":
        is_success, fail_reason = handle_RelVal(args)
    elif args[3] == "SingleMuon":
        is_success, fail_reason = handle_RelVal(args)
    
    if is_success:
        return get_response(t0, "success", fail_reason, args,  "Query proccessed successfully")
    else:
        return get_response(t0, "fail", fail_reason, args,  "Query failed")

if __name__ == "__main__":
    # print(process_query(["0th_index_is__this_file.py","/RelValZMM_14/CMSSW_9_1_1_patch1-PU25ns_91X_upgrade2023_realistic_v3_D17PU140-v1/DQMIO", "/RelValZMM_14/CMSSW_9_3_0_pre3-PU25ns_92X_upgrade2023_realistic_v2_D17PU140-v2/DQMIO"]))
    print(process_query(sys.argv))

    print process_query(["0th_indix_is_this_file.py", "/SingleMuon/Run2017C-PromptReco-v1/DQMIO", "/SingleMuon/Run2017E-PromptReco-v1/DQMIO", "SingleMuon", ""])
