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

def list_of_datasets(wildcardeddataset, short=False):
    if wildcardeddataset.count("/") != 3:
        raise RuntimeError("You need three / in your dataset query")

    _, pd, proc, tier = wildcardeddataset.split("/")
    # url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/datasets?dataset=%s&detail=0" % (get_dbs_instance(wildcardeddataset),wildcardeddataset)
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/datasets?primary_ds_name=%s&processed_ds_name=%s&data_tier_name=%s&detail=0" % (get_dbs_instance(wildcardeddataset),pd,proc,tier)
    ret = get_url_with_cert(url)
    if len(ret) > 0:
        vals = []

        def get_info(d):
            info = dataset_event_count(d["dataset"])
            info["dataset"] = d["dataset"]
            return info

        if short: vals = [d["dataset"] for d in ret]
        else: 
            if len(ret) > 150:
                raise Exception("Getting detailed information for all these datasets (%i) will take too long" % len(ret))

            from multiprocessing.dummy import Pool as ThreadPool 

            pool = ThreadPool(8)
            vals = pool.map(get_info, ret)
            pool.close()
            pool.join()

            return vals
    return []

def get_dataset_files(dataset, run_num=None,lumi_list=[]):
    # return list of 3-tuples (LFN, nevents, size_in_GB) of files in a given dataset
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/files?dataset=%s&validFileOnly=1&detail=1" % (get_dbs_instance(dataset),dataset)
    if run_num and lumi_list:
        url += "&run_num=%i&lumi_list=[%s]" % (run_num, ",".join(map(str,lumi_list)))
    ret = get_url_with_cert(url)
    files = []
    for f in ret:
        files.append( [f['logical_file_name'], f['event_count'], f['file_size']/1.0e9, f['last_modification_date']] )
    return files

def get_dataset_runs(dataset):
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/runs?dataset=%s" % (get_dbs_instance(dataset),dataset)
    return get_url_with_cert(url)[0]["run_num"]

def filelist_to_dict(files, short=False, num=10):
    newfiles = []
    for f in files:
        newfiles.append({"name": f[0], "nevents": f[1], "sizeGB": round(f[2],2), "last_modified":f[3]})
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
        payload = True
        raise Exception("Dataset not specified")

    try:
        if query_type == "basic":
            info = dataset_event_count(entity)
            if not info:
                failed = True
                payload = None
                raise Exception("Dataset not found")
            payload = info

        elif query_type == "files":
            files = get_dataset_files(entity)
            payload = filelist_to_dict(files, short, num=10)

        elif query_type == "listdatasets":
            datasets = list_of_datasets(entity, short)
            if not datasets:
                failed = True
                payload = None
                raise Exception("No datasets found")
            payload = datasets

        elif query_type == "runs":
            payload = get_dataset_runs(entity)

        else:
            failed = True
            payload = None
            raise Exception("Query type not supported")

    except Exception as error:
        failed = True
        fail_reason = str(error)
        payload = None

    finally:
        return json.loads(make_response(arg_dict, payload, failed, fail_reason, warning))

def handle_main(args):

    full_response = handle_query({"query":args["search"], "type":"files", "short":False})

    files = []

    if full_response["response"]["payload"]:
        for obj in full_response["response"]["payload"]:
            if "*" in args["search"]:
                files.append(obj["dataset"])
            else:
                if "SingleMuon" in args["search"] and "PromptReco" in args["search"]:
                    name_split = obj["name"].split("/000/")[1].split("/00000/")[0].split("/")
                    if (len(name_split) > 1):
                        name = int(name_split[0] + name_split[1])
                    else:
                        name = int(name_split[0] + "000")

                    if name not in files: files.append(name)
                else:
                    files.append(obj["name"])
    
    if "SingleMuon" in args["search"] and "PromptReco" in args["search"]:
        try:
            files.sort(key=int)
        except ValueError:
            pass

    full_response["response"]["payload"] = files

    print(json.dumps(full_response))

    return

if __name__=='__main__':

    args = json.loads(sys.argv[1])
    handle_main(args)
    
