#!/usr/bin/python
import cgi
import commands

def inputToDict(form):
    d = {}
    for k in form.keys():
        d[k] = form[k].value
    return d
form = cgi.FieldStorage()
print "Content-type: application/json"
print "Access-Control-Allow-Origin: *\n\n"
inp = inputToDict(form)

arg_str = str(inp)
# arg_str = arg_str.replace("'","\\'")
# arg_str = arg_str.replace("|", "\|")

stat, out = commands.getstatusoutput("./do.sh \"%s\"" % arg_str)
print out
