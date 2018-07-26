#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cgi
import json
import os
import traceback
from autodqm import dqm, compare_hists
from autoref import ref

VARS = {}


def handle_request(req):
    err = None
    try:
        load_vars()
        if req['type'] == "fetch_run":
            data = fetch_run(req['series'], req['sample'], req['run'])
        elif req['type'] == "process":
            data = process(req['subsystem'],
                           req['data_series'],
                           req['data_sample'],
                           req['data_run'],
                           req['ref_series'],
                           req['ref_sample'],
                           req['ref_run'])
        elif req['type'] == "get_subsystems":
            data = get_subsystems()
        elif req['type'] == "get_series":
            data = get_series()
        elif req['type'] == "get_samples":
            data = get_samples(req['series'])
        elif req['type'] == "get_runs":
            data = get_runs(req['series'], req['sample'])
        elif req['type'] == "get_ref":
            data = get_ref(req['data_run'], get_runs(req['series'], req['sample']))
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
    dqm.fetch_run(series, sample, run, VARS['CERT'], db=VARS['DB'])
    return {}


def process(subsystem,
            data_series, data_sample, data_run,
            ref_series, ref_sample, ref_run):

    # Get root file paths
    data_path = dqm.fetch_run(data_series, data_sample, data_run,
                              VARS['CERT'], db=VARS['DB'])
    ref_path = dqm.fetch_run(ref_series, ref_sample, ref_run,
                             VARS['CERT'],  db=VARS['DB'])

    # Get config and results/plugins directories
    results_dir = os.path.join(VARS['PUBLIC'], 'results')
    plugin_dir = VARS['PLUGINS']
    with open(VARS['CONFIG']) as config_file:
        config = json.load(config_file)

    # Process this query
    results = compare_hists.process(config, subsystem,
                                    data_series, data_sample,
                                    data_run, data_path,
                                    ref_series, ref_sample,
                                    ref_run, ref_path,
                                    output_dir=results_dir,
                                    plugin_dir=plugin_dir)

    # Relativize the results paths
    def relativize(p): return os.path.join(
        'results', os.path.relpath(p, results_dir))
    for r in results:
        r['pdf_path'] = relativize(r['pdf_path'])
        r['json_path'] = relativize(r['json_path'])
        r['png_path'] = relativize(r['png_path'])

    return {'items': results}


def get_subsystems():
    with open(VARS['CONFIG']) as config_file:
        config = json.load(config_file)
    return {'items': [{"name": s} for s in config]}


def get_series():
    rows = dqm.fetch_series_list(VARS['CERT'], cache=VARS['CACHE'])
    return {'items': [r._asdict() for r in rows]}


def get_samples(series):
    rows = dqm.fetch_sample_list(series, VARS['CERT'], cache=VARS['CACHE'])
    return {'items': [r._asdict() for r in rows]}


def get_runs(series, sample):
    rows = dqm.fetch_run_list(series, sample,
                              VARS['CERT'], cache=VARS['CACHE'])
    return {'items': [r._asdict() for r in rows]}

def get_ref(data_run, get_runs_out):
    ref_runs = []
    for row in get_runs_out['items']:
        ref_runs.append(row['name'])
    refs = ref.fetch_ref(data_run, ref_runs)
    return {'items': refs}


def load_vars():
    try:
        VARS.update({
            'SSLCERT': os.environ['ADQM_SSLCERT'],
            'SSLKEY': os.environ['ADQM_SSLKEY'],
            'DB': os.environ['ADQM_DB'],
            'PUBLIC': os.environ['ADQM_PUBLIC'],
            'CONFIG': os.environ['ADQM_CONFIG'],
            'PLUGINS': os.environ['ADQM_PLUGINS']
        })
        VARS['CERT'] = (VARS['SSLCERT'], VARS['SSLKEY'])
        VARS['CACHE'] = os.path.join(VARS['DB'], 'dqm_offline')
    except Exception as e:
        raise ServerError("Server incorrectly configured: {}".format(e))


class error(Exception):
    pass


class ServerError(error):
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
