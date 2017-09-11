#!/usr/bin/env python

import urllib, urllib2, json
import sys
import argparse

"""
examples:
       dis_client.py -t snt "*,cms3tag=CMS3_V08-00-01 | grep dataset_name,nevents_in, nevents_out"
           - this searches for all samples with the above tag in all Twikis and only prints out dataset_name, nevents_out

       dis_client.py /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
           - prints out basic information (nevents, file size, number of files, number of lumi blocks) for this dataset

       dis_client.py -t files /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
           - prints out filesize, nevents, location for a handful of files for this dataset

       dis_client.py -t files -d /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
           - prints out above information for ALL files

Or you can import dis_client and make a query using online syntax and get a json via:
       dis_client.query(q="..." [, typ="basic"] [, detail=False])
"""

BASE_URL_PATTERN = "http://uaf-{NUM}.t2.ucsd.edu/~namin/makers/disMaker/handler.py"

def query(q, typ="basic", detail=False):
    url_pattern = '%s?%s' % (BASE_URL_PATTERN, urllib.urlencode({"query": q, "type": typ, "short": "" if detail else "short"}))

    data = {}
    # try all uafs
    for num in map(str,[8,10,6,3,4,5]):
        try:
            url = url_pattern.replace("{NUM}",num)
            content =  urllib2.urlopen(url).read() 
            data = json.loads(content)
            break
        except: print "Failed to perform URL fetching and decoding (using uaf-%s)!" % num

    return data

        
def get_output_string(q, typ="basic", detail=False, show_json=False):
    buff = ""
    data = query(q, typ, detail)

    if not data:
        return "URL fetch/decode failure"

    if data["response"]["status"] != "success":
        return "DIS failure: %s" % data["response"]["fail_reason"]

    data = data["response"]["payload"]
    
    if show_json:
        return json.dumps(data, indent=4)


    if type(data) == dict:
        if "files" in data: data = data["files"]


    if type(data) == list:
        for elem in data:
            if type(elem) == dict:
                for key in elem:
                    buff += "%s:%s\n" % (key, elem[key])
            else:
                buff += str(elem)
            buff += "\n"
    elif type(data) == dict:
        for key in data:
            buff += "%s: %s\n\n" % (key, data[key])

    return buff

def test(one=False):

    queries = [
    {"q":"/*/CMSSW_8_0_5*RelVal*/MINIAOD","typ":"basic","detail":False},
    {"q":"/SingleMuon/CMSSW_8_0_5-80X_dataRun2_relval_v9_RelVal_sigMu2015C-v1/MINIAOD","typ":"files","detail":True},
    {"q":"/GJets*/*/*","typ":"snt","detail":True},
    {"q":"/GJets*/*/* | grep cms3tag,dataset_name","typ":"snt","detail":False},
    {"q":"* | grep nevents_out","typ":"snt","detail":False},
    {"q":"/GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM","typ":"mcm","detail":True},
    ]
    if one: queries = queries[3:4]
    for q_params in queries:
        print get_output_string(**q_params)

if __name__ == '__main__':
    
    # test(one=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="query")
    parser.add_argument("-t", "--type", help="type of query")
    parser.add_argument("-d", "--detail", help="show more detailed information", action="store_true")
    parser.add_argument("-j", "--json", help="show output as full json", action="store_true")
    args = parser.parse_args()
    if not args.type: args.type = "basic"
    print get_output_string(args.query, typ=args.type, detail=args.detail, show_json=args.json)

