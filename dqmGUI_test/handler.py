#!/usr/bin/python
import cgi
import commands

# def inputToDict(form):
#     d = {}
#     for k in form.keys():
#         d[k] = form[k].value
#     return d
def inputToList(form):
    l = []
    for k in form.keys():
        l.append(form[k].value)
    return l
form = cgi.FieldStorage()
print "Content-type: application/json"
print "Access-Control-Allow-Origin: *\n\n"
# inp = inputToDict(form)
inp = inputToList(form)

# arg_str = str(inp)
# arg_str = arg_str.replace("'","\\'")
# arg_str = arg_str.replace("|", "\|")

args = "./do.sh"
for i in inp:
    args += " {0}".format(i)

stat, out = commands.getstatusoutput(args)
# stat, out = commands.getstatusoutput("./do.sh \"%s\"" % arg_str)
# stat, out = commands.getstatusoutput("./do.sh /RelValZMM_14/CMSSW_9_3_0_pre3-PU25ns_92X_upgrade2023_realistic_v2_D17PU140-v2/DQMIO /RelValZMM_14/CMSSW_9_1_1_patch1-PU25ns_91X_upgrade2023_realistic_v3_D17PU140-v1/DQMIO")
# stat, out = commands.getstatusoutput(args)
print out
