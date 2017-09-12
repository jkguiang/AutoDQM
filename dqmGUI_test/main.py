import sys
import json
import subprocess
import ROOT

import dis_client
import AutoDQM

# Ultimately, we want payload to be the name of the html file with plots on it
def get_response(is_fail, query, timestamp, status, warning, payload):
    query = query
    timestamp = 0
    status = "success"
    fail_reason = None
    if is_fail == True:
        status = "failed"
        fail_reason = "Failed, no reasons implemented yet"
    warning = None
    payload = payload
    return json.dumps( { "query": query, "timestamp": timestamp, "response": { "status": status, "fail_reason": fail_reason, "warning": warning, "payload": payload } } )

def compile_hists(new_dir):
    for path in new_dir:
        f = ROOT.TFile(path)
        t = f.Get("TH2Fs")

        old_h = {}

        for event in tqdm(t):
            path = str(event.FullName)
            name = str(event.Value.GetName())

            # Only look at muon paths
            if not ("CSC/CSCOfflineMonitor" in path): continue
            if type(event.Value) != ROOT.TH1F: continue

            if name not in old_h:
                old_h[name] = event.Value.Clone(name)
            else:
                old_h[name].Add(event.Value)

    return old_h

def get_hists(fdir, rdir):
    f_hists = compile_hists(fdir)
    r_hists = compile_hists(rdir)

    subprocess.call("make_html.sh setup")

    # AutoDQM takes dicts of data and ref hists, 'ID' of sample (i.e. PU200, noPU, etc.) <- For now, and target directory (currently using cwd)
    AutoDQM.autodqm(f_hists, r_hists, "TEST", "")

    subprocess.call("make_html.sh updt")

    return

def get_files(path, opt):

    response = dis_client.query(q=path, typ="files", detail=True)
    data = response["response"]["payload"]
    to_xrd = ""

    for tfile in data:
        to_xrd.append(" "+t_file)

    subprocess.call("get_xrd.sh {0}{1}".format(opt, to_xrd))

    return


def process_query(args):

    # Generate root files via bash subprocess
    get_files(args[1], "data")
    get_files(args[2], "ref")

    # Root files should now be in data and ref directories
    get_hists("/data", "/ref")

    return get_response(False, args, timestamp, None, "TEST")

if __name__ == "__main__":
    print(process_query(sys.argv))
