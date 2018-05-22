#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import traceback
import fetch
import compare_hists
import search


def get_response(t0, status, fail_reason, tb, query, payload):
    duration = time.time() - t0
    return json.dumps({"query": query, "start": t0, "duration": duration, "response": {"status": status, "fail_reason": str(fail_reason), "traceback": str(tb)}})


def get_subsystems():
    with open(os.getenv('ADQM_CONFIG')) as config_file:
        config = json.load(config_file)
    return [{"name": s} for s in config]


def check(is_success, fail_reason):
    if not is_success:
        raise Exception('Error: {0}'.format(fail_reason))
    else:
        return None


def handle_args(args):

    # Values for tracking script's progress
    is_success = False
    fail_reason = None

    try:
        if args["type"] == "retrieve_data":
            is_success, fail_reason = fetch.fetch(
                args["data_series"], args["data_sample"], args["data_run"])
            check(is_success, fail_reason)
        elif args["type"] == "retrieve_ref":
            is_success, fail_reason = fetch.fetch(
                args["ref_series"], args["ref_sample"], args["ref_run"])
            check(is_success, fail_reason)

        elif args["type"] == "process":
            is_success, fail_reason = compare_hists.process(
                args["user_id"],
                args["subsystem"],
                {"series": args["data_series"],
                 "sample": args["data_sample"],
                 "run": args["data_run"]},
                {"series": args["ref_series"],
                 "sample": args["ref_sample"],
                 "run": args["ref_run"]}
            )
            check(is_success, 'get_hists')

    except Exception as error:
        fail_reason = str(error)
        return is_success, fail_reason, traceback.format_exc()

    return is_success, fail_reason, None


def process_query(args):
    t0 = time.time()

    is_success, fail_reason, tb = handle_args(args)

    if is_success and fail_reason == None:
        return get_response(t0, "success", fail_reason, tb, args,  "Query proccessed successfully")
    else:
        return get_response(t0, "fail", fail_reason, tb, args,  "Query failed")


if __name__ == "__main__":
    args = json.loads(sys.argv[1])
    print(process_query(args))
