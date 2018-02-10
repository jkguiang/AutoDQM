#!/usr/bin/python
import cgi
import json
import commands

query_type = "" # This stores query type, MUST be passed first to do.sh

def inputToDict(form):
    new_dict = {}
    for k in form.keys():
        new_dict[str(k)] = str(form[k].value)
    return new_dict

form = cgi.FieldStorage()
print "Content-type: application/json"
print "Access-Control-Allow-Origin: *\n\n"
inp = inputToDict(form)

args = ("./do.sh {0} {1} '{2}'".format(inp["type"], inp["user_id"], str(json.dumps(inp))))

stat, out = commands.getstatusoutput(args)
print out
