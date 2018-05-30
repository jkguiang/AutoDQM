#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import traceback
import fetch
import compare_hists


def handle_request(req):
    err = None
    try:
        if req['type'] == "fetch_run":
            data = fetch_run(req['series'], req['sample'], req['run'])
        elif req['type'] == "process":
            data = process(req['uid'], req['subsystem'],
                           req['data_series'], req['data_sample'], req['data_run'],
                           req['ref_series'], req['ref_sample'], req['ref_run'])
        elif req['type'] == "get_subsystems":
            data = get_subsystems()
        elif req['type'] == "get_series":
            data = get_series()
        elif req['type'] == "get_samples":
            data = get_samples(req['series'])
        elif req['type'] == "get_runs":
            data = get_samples(req['series'], req['sample'])
        else:
            raise error
    except Exception as e:
        err = e
        tb = traceback.format_exc()
    finally:
        res = {}
        if error:
            res['error'] = {
                'message': str(err)
                'traceback': tb
            }
        else:
            res['data'] = data
        return res


def fetch_run(series, sample, run):
    fetch.fetch(series, sample, run)
    return {}


def process(uid, subsystem,
            data_series, data_sample, data_run,
            ref_series, ref_sample, ref_run):
    data = {}
    data['items'] = compare_hists.process(
        uid, subsystem
        {"series": data_series,
         "sample": data_sample,
         "run": data_run}
        {"series": ref_series,
         "sample": ref_sample,
         "run": ref_run})
    return data


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
    for k in form.keys():
        req[str(k)] = str(cgi_req[k].value)

    res = handle_request(req)

    print("Content-type: application/json")
    print("Access-Control-Allow-Origin: *")
    print()
    print(json.dumps(res))
