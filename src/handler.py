#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cgi
import json
import commands
from subprocess import check_output
from fetch import get_series, get_samples, get_runs
from index import get_subsystems
import traceback

def inputToDict(form):
    new_dict = {}
    for k in form.keys():
        new_dict[str(k)] = str(form[k].value)
    return new_dict


if __name__ == "__main__":
    form = cgi.FieldStorage()
    inp = inputToDict(form)

    try:
        reqType = inp["type"]

        if reqType == "retrieve_data" or reqType == "retrieve_ref" or reqType == "process":
            out = check_output(["python", "index.py", json.dumps(inp)])
        elif reqType == "getSeries":
            out = json.dumps({
                "response": {
                    "status": "success",
                    "fail_reason": "",
                    "series": get_series()}
            }, default=str)
        elif reqType == "getSamples":
            out = json.dumps({
                "response": {
                    "status": "success",
                    "fail_reason": "",
                    "samples": get_samples(inp["series"])}
            }, default=str)
        elif reqType == "getRuns":
            out = json.dumps({
                "response": {
                    "status": "success",
                    "fail_reason": "",
                    "runs": get_runs(inp["series"], inp["sample"])}
            }, default=str)
        elif reqType == "getSubsystems":
            out = json.dumps({
                "response": {
                    "status": "success",
                    "fail_reason": "",
                    "subsystems": get_subsystems()}
            }, default=str)
        else:
            raise Exception("Request type not found: {0}".format(reqType))
    except Exception as e:
        out = json.dumps({
            "response": {
                "status": "fail",
                "fail_reason": str(e),
                "traceback": str(traceback.format_exc())
            }})

    print "Content-type: application/json"
    print "Access-Control-Allow-Origin: *\n\n"
    print out
