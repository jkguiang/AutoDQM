import os
import sys
import ast
import json
import traceback
import glob
import time
import pycurl 
import StringIO 
import datetime

import commands

def get(cmd, returnStatus=False):
    status, out = commands.getstatusoutput(cmd)
    if returnStatus: return status, out
    else: return out

def cmd(cmd, returnStatus=False):
    status, out = commands.getstatusoutput(cmd)
    if returnStatus: return status, out
    else: return out

def proxy_hours_left():
    try:
        info = get("voms-proxy-info")
        hours = int(info.split("timeleft")[-1].strip().split(":")[1])
    except: hours = 0
    return hours

def proxy_renew():
    # http://www.t2.ucsd.edu/tastwiki/bin/view/CMS/LongLivedProxy
    cert_file = "/home/users/{0}/.globus/proxy_for_{0}.file".format(get("whoami").strip())
    if os.path.exists(cert_file): cmd("voms-proxy-init -q -voms cms -hours 120 -valid=120:0 -cert=%s" % cert_file)
    else: cmd("voms-proxy-init -hours 9876543:0 -out=%s" % cert_file)

def get_proxy_file():
    cert_file = '/tmp/x509up_u%s' % str(os.getuid()) # TODO: check that this is the same as `voms-proxy-info -path`
    return cert_file

def get_url_with_cert(url, return_raw=False):
    # get json from a dbs url (API ref is at https://cmsweb.cern.ch/dbs/prod/global/DBSReader/)
    b = StringIO.StringIO() 
    c = pycurl.Curl() 
    cert = get_proxy_file()
    c.setopt(pycurl.WRITEFUNCTION, b.write) 
    c.setopt(pycurl.CAPATH, '/etc/grid-security/certificates') 
    c.unsetopt(pycurl.CAINFO)
    c.setopt(pycurl.SSLCERT, cert)
    c.setopt(pycurl.URL, url) 
    c.perform() 
    s = b.getvalue()
    if return_raw: return s
    s = s.replace("null","None")
    ret = ast.literal_eval(s)
    return ret

def get_dbs_instance(dataset):
    if dataset.endswith("/USER"): return "phys03"
    elif "Nick" in dataset: return "phys03"
    else: return "global"

def dataset_event_count(dataset):
    # get event count and other information from dataset
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/filesummaries?dataset=%s&validFileOnly=1" % (get_dbs_instance(dataset),dataset)
    ret = get_url_with_cert(url)
    if len(ret) > 0:
        if ret[0]:
            return { "nevents": ret[0]['num_event'], "filesizeGB": round(ret[0]['file_size']/1.9e9,2), "nfiles": ret[0]['num_file'], "nlumis": ret[0]['num_lumi'] }
    return None

def get_dataset_files(dataset, run_num=None,lumi_list=[]):
    # return list of 3-tuples (LFN, nevents, size_in_GB) of files in a given dataset
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/files?dataset=%s&validFileOnly=1&detail=1" % (get_dbs_instance(dataset),dataset)
    if run_num and lumi_list:
        url += "&run_num=%i&lumi_list=[%s]" % (run_num, ",".join(map(str,lumi_list)))
    ret = get_url_with_cert(url)
    files = []
    for f in ret:
        files.append( [f['logical_file_name'], f['event_count'], f['file_size']/1.0e9] )
    return files

def get_dataset_runs(dataset):
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/runs?dataset=%s" % (get_dbs_instance(dataset),dataset)
    return get_url_with_cert(url)[0]["run_num"]

def filelist_to_dict(files, short=False, num=10):
    newfiles = []
    for f in files:
        newfiles.append({"name": f[0], "nevents": f[1], "sizeGB": round(f[2],2)})
    if short: newfiles = newfiles[:num]
    return newfiles

def make_response(query, payload, failed, fail_reason, warning):
    status = "success"
    if failed: status = "failed"

    timestamp = int(time.time())
    return json.dumps( { "query": query, "timestamp": timestamp, "response": { "status": status, "fail_reason": fail_reason, "warning": warning, "payload": payload } } )
    # return { "query": query, "response": { "status": status, "fail_reason": fail_reason, "payload": payload } }


def handle_query(arg_dict):

    query_type = arg_dict.get("type","basic")
    query = arg_dict.get("query", None).strip()
    short = arg_dict.get("short", False)

    entity = query.strip()

    failed = False
    fail_reason = ""
    warning = ""
    payload = {}

    if "*" in entity and query_type in ["basic","files"]:
        query_type = "listdatasets"

    if query_type in ["basic", "files", "listdatasets", "mcm", "driver", "lhe", "parents", "dbs"]:
        if proxy_hours_left() < 5: proxy_renew()

    if not entity:
        failed = True
        fail_reason = "Dataset not specified"


    if query_type == "basic":
        info = dataset_event_count(entity)
        if not info:
            failed = True
            fail_reason = "Dataset not found"
        payload = info

    elif query_type == "files":
        files = get_dataset_files(entity)
        payload = filelist_to_dict(files, short, num=10)

    elif query_type == "runs":
        payload = get_dataset_runs(entity)

    else:
        failed = True
        fail_reason = "Query type not supported"
        payload = None

    return json.loads(make_response(arg_dict, payload, failed, fail_reason, warning))

if __name__=='__main__':

    arg_dict = {"query":"/SingleMuon/Run2017C-PromptReco-v3/DQMIO", "type":"files", "short":False}
    # arg_dict = {"query": "/TChiChi_mChi-150_mLSP-1_step1/namin-TChiChi_mChi-150_mLSP-1_step1-695fadc5ae5b65c0e37b75e981d30125/USER", "type":"files"}
    # arg_dict = {"query": "/TChiNeu*/namin-TChiNeu*/USER", "type":"files"}
    # arg_dict = {"type": "snt", "query": "/TChiChi_mChi-150_mLSP-1_step1/namin-TChiChi_mChi-150_mLSP-1_step2_miniAOD-eb69b0448a13fda070ca35fd76ab4e24/USER"}
    # arg_dict = {"type": "snt", "query": "/TChiChi*/*/USER", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/TChiChi*/*/USER, gtag=*74X*", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/GJet*HT-400*/*/*", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/GJet*HT-400*/*/*, gtag=*74X*, cms3tag=*07*", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/GJet*HT-400*/*/*, gtag=*74X*, cms3tag=*07* | grep nevents_out,dataset_name", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/G* | grep cms3tag"}
    # arg_dict = {"type": "driver", "query": "/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM"}
    # arg_dict = {"type": "lhe", "query": "/SMS-T5qqqqWW_mGl-600to800_mLSP-0to725_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15MiniAODv2-FastAsympt25ns_74X_mcRun2_asymptotic_v2-v1/MINIAODSIM"}
    # arg_dict = {"type": "driver", "query": "/SMS-T5qqqqWW_mGl-600to800_mLSP-0to725_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15MiniAODv2-FastAsympt25ns_74X_mcRun2_asymptotic_v2-v1/MINIAODSIM"}
    # arg_dict = {"type": "parents", "query": "/SMS-T1tttt_mGluino-1500_mLSP-100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv1-PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/MINIAODSIM"}
    # arg_dict = {"type": "mcm", "query": "/QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM | grep cross_section", "short":"short"}
    # arg_dict = {"type": "mcm", "query": "/QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM", "short":"short"}
    # arg_dict = {"type": "update_snt", "query": "dataset_name=test,cms3tag=CMS3_V07-06-03_MC,sample_type=CMS3,gtag=test,location=/hadoop/crap/crap/", "short":"short"}
    # arg_dict = {"type": "snt", "query": "test", "short":"short"}
    # arg_dict = {"type": "basic", "query": "/SingleElectron/Run2016B-PromptReco-v1/MINIAOD"}
    # arg_dict = {"type": "dbs", "query": "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/files?dataset=/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring16MiniAODv1-PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/MINIAODSIM&detail=1&lumi_list=[134007]&run_num=1"}
    # arg_dict = {"type": "runs", "query": "/SinglePhoton/Run2016E-PromptReco-v2/MINIAOD"}
    # arg_dict = {"type": "pick", "query": "/MET/Run2016D-PromptReco-v2/MINIAOD,276524:9999:2340928340,276525:2892:550862893,276525:2893:823485588,276318:300:234982340,276318:200:234982340"}
    # arg_dict = {"type": "pick_cms3", "query": "/MET/Run2016D-PromptReco-v2/MINIAOD,276524:9999:2340928340,276525:2892:550862893,276525:2893:823485588,276318:300:234982340,276318:200:234982340"}
    # arg_dict = {"type": "pick_cms3", "query": "/DoubleEG/Run2016C-23Sep2016-v1/MINIAOD,275912:91:164211755", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/WJetsToLNu_TuneCUETP8M1_13TeV-madgr*"}
    # arg_dict = {"type": "sites", "query": "/SingleMuon/Run2016B-PromptReco-v2/MINIAOD"}
    # arg_dict = {"type": "sites", "query": "/store/data/Run2017B/MET/MINIAOD/PromptReco-v1/000/297/562/00000/A456D6BA-BA5C-E711-A4F1-02163E0133C4.root"}

    if not arg_dict:
        arg_dict_str = sys.argv[1]
        arg_dict = ast.literal_eval(arg_dict_str)

    response = json.loads(handle_query(arg_dict))
    data = response["response"]["payload"]

    for tfile in data:
        print(tfile["name"])

