#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cgi
import compare_hists
import fetch
import json
import os
import traceback


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


def fetch_run(series, sample, run):
    fetch.fetch(series, sample, run)
    return {}


def process(subsystem,
            data_series, data_sample, data_run,
            ref_series, ref_sample, ref_run):
    results_dir = os.path.join(os.getenv('ADQM_PUBLIC'), 'results')
    results = compare_hists.process(subsystem,
                                    data_series, data_sample, data_run,
                                    ref_series, ref_sample, ref_run,
                                    output_dir=results_dir)

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
    return {'items': fetch.get_series()}


def get_samples(series):
    return {'items': fetch.get_samples(series)}


def get_runs(series, sample):
    return {'items': fetch.get_runs(series, sample)}


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
