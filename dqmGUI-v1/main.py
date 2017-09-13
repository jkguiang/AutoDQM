import os
import sys
import json
import time
import ROOT
import subprocess

import dis_client
import AutoDQM

# Ultimately, we want payload to be the name of the html file with plots on it
def get_response(t0, status, fail_reason, query, payload):
    timestamp = time.time()
    duration = timestamp - t0
    warning = None
    return json.dumps( { "query": query, "timestamp": timestamp, "duration":duration, "response": { "status": status, "fail_reason": fail_reason, "warning": warning, "payload": payload } } )

def compile_hists(new_dir):
    old_h = {}
    dir_list = os.listdir(new_dir)
    counter = 0
    for path in dir_list:
        f = ROOT.TFile(new_dir + "/" + path)
        t = f.Get("TH2Fs")

        for event in t:
            path = str(event.FullName)
            name = str(event.Value.GetName())

            # Only look at muon paths
            if not ("CSC/CSCOfflineMonitor" in path): continue
            if type(event.Value) != ROOT.TH2F: continue

            if name not in old_h:
                old_h[name] = event.Value.Clone(name)
                old_h[name].SetDirectory(0)
            else:
                old_h[name].Add(event.Value)

        f.Close()

    return old_h

def get_hists(fdir, rdir, f_id):
    f_hists = compile_hists(fdir)
    r_hists = compile_hists(rdir)

    subprocess.check_call(["{0}/make_html.sh".format(os.getcwd()), "setup"])

    # AutoDQM takes dicts of data and ref hists, 'ID' of sample (i.e. PU200, noPU, etc. May change this later), and target directory (currently using cwd)
    AutoDQM.autodqm(f_hists, r_hists, f_id, os.getcwd())

    subprocess.check_call(["{0}/make_html.sh".format(os.getcwd()), "updt"])

    return

def get_id(path):
    return path.split("/DQMIO")[0].split("_")[-1].split("-")[0]

def get_files(path, opt):

    response = dis_client.query(q=path, typ="files", detail=True)
    data = response["response"]["payload"]
    xrd_args = ["{0}/get_xrd.sh".format(os.getcwd()), opt]

    for tfile in data:
        xrd_args.append(tfile["name"])

    subprocess.check_call(xrd_args)

    return


def process_query(args):
    t0 = time.time()

    # Generate root files via bash subprocess
    get_files(str(args[1]), "data")
    get_files(str(args[2]), "ref")

    if (get_id(args[1]) != get_id(args[2])):
        # get_response : (t0, status, fail_reason, query, payload)
        return get_response(t0, "failed", "Error: Pile-up of data is not equal to reference pile-up.", 
                            args, "Data ID: {0}, Ref ID: {1}".format(get_id(args[1]), get_id(args[2])))

    # Root files should now be in data and ref directories
    get_hists("{0}/data".format(os.getcwd()), "{0}/ref".format(os.getcwd()), get_id(args[1]))

    return get_response(t0, "success", None, args,  "Query proccessed successfully")

if __name__ == "__main__":
    # print(process_query(["0_index_is_file.py","/RelValZMM_14/CMSSW_9_1_1_patch1-PU25ns_91X_upgrade2023_realistic_v3_D17PU140-v1/DQMIO", "/RelValZMM_14/CMSSW_9_3_0_pre3-PU25ns_92X_upgrade2023_realistic_v2_D17PU140-v2/DQMIO"]))
    print(process_query(sys.argv))
