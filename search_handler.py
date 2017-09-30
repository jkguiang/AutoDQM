#!/usr/bin/python
import cgi
import commands

def inputToList(form):
    l = []
    for k in form.keys():
        l.append(form[k].value)
    return l
form = cgi.FieldStorage()
print "Content-type: application/json"
print "Access-Control-Allow-Origin: *\n\n"
inp = inputToList(form)

args = "./do_search.sh"
for i in inp:
    args += " {0}".format(i)

stat, out = commands.getstatusoutput(args)
print out
