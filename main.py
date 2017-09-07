import dis_client

# User input
serial = "9_3_0"
patch = "pre3-92X"
version = "v2_2023D17noPU-v1"

response = dis_client.query(q="/RelValZMM_14/CMSSW_{0}_{1}_upgrade2023_realistic_{2}/DQMIO".format(serial, patch, version), typ="files", detail=True)
# data: list with file info, each file is contained in a dict, data[i]["name"] gives root file for xrdcp
data = response["response"]["payload"]

print response
print data
