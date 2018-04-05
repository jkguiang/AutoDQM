#!/usr/bin/python
import cgi
import json
import commands
from subprocess import check_output


def inputToDict(form):
    new_dict = {}
    for k in form.keys():
        new_dict[str(k)] = str(form[k].value)
    return new_dict


if __name__ == "__main__":
    form = cgi.FieldStorage()
    inp = inputToDict(form)
    reqType = inp["type"]

    if reqType == "retrieve_data" or reqType == "retrieve_ref" or reqType == "process":
        out = check_output(["python", "index.py", json.dumps(inp)])
    elif reqType == "search":
        out = check_output(["python", "search.py", json.dumps(inp)])
    elif reqType == "refresh":
        out = check_output(["python", "database.py", "map"])
    else:
        out = json.dumps({
            "response": {
                "status": "fail",
                "fail_reason": "Request type not found: {0}".format(reqType)
            }})

    print "Content-type: application/json"
    print "Access-Control-Allow-Origin: *\n\n"
    print out
