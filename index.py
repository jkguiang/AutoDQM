#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cgi
import json
import os
import traceback
from autodqm import fetch, compare_hists
from autodqm.cerncert import CernCert


def handle_request(req):
    err = None
    try:
        if req['type'] == "fetch_run":
            data = fetch_run(req['series'], req['sample'], req['run'])
        elif req['type'] == "process":
            data = process(req['subsystem'],
                           req['data_series'], req['data_sample'], req['data_run'],
                           req['ref_series'], req['ref_sample'], req['ref_run'])
        elif req['type'] == "get_subsystems":
            data = get_subsystems()
        elif req['type'] == "get_series":
            data = get_series()
        elif req['type'] == "get_samples":
            data = get_samples(req['series'])
        elif req['type'] == "get_runs":
            data = get_runs(req['series'], req['sample'])
        else:
            raise error
    except Exception as e:
        err = e
        tb = traceback.format_exc()
    finally:
        res = {}
        if err:
            res['error'] = {
                'message': str(err),
                'traceback': tb
            }
        else:
            res['data'] = data
        return res


def make_cert():
    return CernCert(sslcert=os.getenv('ADQM_SSLCERT'),
                    sslkey=os.getenv('ADQM_SSLKEY'),
                    cainfo=os.getenv('ADQM_CERNCA'))


def fetch_run(series, sample, run):
    cert = make_cert()
    fetch.fetch(cert, series, sample, run, db=os.getenv('ADQM_DB'))
    return {}


def process(subsystem,
            data_series, data_sample, data_run,
            ref_series, ref_sample, ref_run):

    # Get root file paths
    cert = make_cert()
    data_path = fetch.fetch(cert,
                            data_series, data_sample, data_run,
                            db=os.getenv('ADQM_DB'))
    ref_path = fetch.fetch(cert,
                           ref_series, ref_sample, ref_run,
                           db=os.getenv('ADQM_DB'))

    # Get config and results/plugins directories
    results_dir = os.path.join(os.getenv('ADQM_PUBLIC'), 'results')
    plugin_dir = os.getenv('ADQM_PLUGINS')
    with open(os.getenv('ADQM_CONFIG')) as config_file:
        config = json.load(config_file)

    # Process this query
    results = compare_hists.process(config, subsystem,
                                    data_series, data_sample, data_run, data_path,
                                    ref_series, ref_sample, ref_run, ref_path,
                                    output_dir=results_dir, plugin_dir=plugin_dir)

    # Relativize the results paths
    def relativize(p): return os.path.join(
        'results', os.path.relpath(p, results_dir))
    for r in results:
        r['pdf_path'] = relativize(r['pdf_path'])
        r['json_path'] = relativize(r['json_path'])
        r['png_path'] = relativize(r['png_path'])

    return {'items': results}


def get_subsystems():
    with open(os.getenv('ADQM_CONFIG')) as config_file:
        config = json.load(config_file)
    return {'items': [{"name": s} for s in config]}


def get_series():
    cert = make_cert()
    return {'items': fetch.get_series(cert)}


def get_samples(series):
    cert = make_cert()
    return {'items': fetch.get_samples(cert, series)}


def get_runs(series, sample):
    cert = make_cert()
    return {'items': fetch.get_runs(cert, series, sample)}


class error(Exception):
    pass


if __name__ == "__main__":
    cgi_req = cgi.FieldStorage()

    req = {}
    for k in cgi_req.keys():
        req[str(k)] = str(cgi_req[k].value)

    res = handle_request(req)

    print("Content-type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("")
    print(json.dumps(res))
