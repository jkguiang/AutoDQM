import ROOT
import sys
import dis_client
from tqdm import tqdm

def get_files(args):
    # Passed in full path
    if len(args) == 2:
       response = dis_client.query(q=args[1], typ="files", detail=True)
       # data: list with file info, each file is contained in a dict, data[i]["name"] gives root file for xrdcp
       data = response["response"]["payload"]

    elif len(args) == 4:
        sample = args[1]
        patch = args[2]
        vers = args[3]
        response = dis_client.query(q="/{0}/CMSSW_{1}_realistic_{2}/DQMIO".format(sample, patch, version), typ="files", detail=True)
        # data: list with file info, each file is contained in a dict, data[i]["name"] gives root file for xrdcp
        data = response["response"]["payload"]

    else:
        print("Failed, too few/too many args")
        return

    return data

def get_histos():
    f = ROOT.TFile("92B50E21-B94A-E711-B3B4-0CC47A78A4A6.root")
    t = f.Get("TH1Fs")

    old_h = {}

    title_count = []
    hcount = 0
    titles = {}

    for event in tqdm(t):
        path = str(event.FullName)
        name = str(event.Value.GetName())


        # Only look at muon paths
        if not ("CSC/CSCOfflineMonitor" in path): continue
        if type(event.Value) != ROOT.TH1F: continue
        hcount += 1

        if name not in old_h:
            old_h[name] = event.Value.Clone(name)
            titles[name] = 0

            if old_h[name].GetTitle() not in titles:
                title_count.append(old_h[name].GetTitle())

        else:

            old_h[name].Add(event.Value)
            titles[name] += 1

    print old_h.keys()

    # plot 3 hists to check
    c1 = ROOT.TCanvas()
    for ihist,h1 in enumerate(old_h.values()[:3]):
        h1.Draw()
        # c1.SaveAs("hist_{}.pdf".format(ihist))
        print "saved",h1.GetTitle()

    print(len(old_h))

if __name__ == "__main__":
    if "*" in sys.argv:
        get_list(sys.argv)
        print(0)

    elif "get" in sys.argv:
        get_histos()
        print(1)

    else:
        data = get_files(sys.argv)
        print(data)
