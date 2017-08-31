import ROOT
import os
from tqdm import tqdm

# Parsing Functions -------

# Scan 1D Hist, plot Pull hist and compute Chi^2
def scan_1D(f_hist, r_hist):
    c = ROOT.TCanvas('c', 'Pull')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
    ROOT.gStyle.SetNumberContours(255)

    chi2 = 0
    nBins = 0
    pull_hist = r_hist.Clone("pull_hist")
    pull_hist.Reset()

    # Normalize f_hist
    f_hist.Scale(r_hist.GetEntries()/f_hist.GetEntries())

    for x in range(1, r_hist.GetNbinsX()+1):

        # Bin 1 data
        bin1 = f_hist.GetBinContent(x)
        bin1err = f_hist.GetBinError(x)

        # Bin 2 data
        bin2 = r_hist.GetBinContent(x)
        bin2err = r_hist.GetBinError(x)

        nBins += 1
        if bin1err == 0 and bin2err == 0:
            continue

        new_pull = pull(bin1, bin1err, bin2, bin2err)

        # Sum pulls
        chi2 += new_pull**2

        # Fill Pull Histogram
        pull_hist.SetBinContent(x, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    # Plot pull hist
    pull_hist.SetFillColor(ROOT.kGreen)
    pull_hist.SetLineColor(ROOT.kBlack)
    pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
    pull_hist.Draw("hist")

    # DEBUG
    # print("Chi2: {0}".format(chi2))

    return chi2

# Scan 2D Hist, plot Pull hist and compute Chi^2
def scan_2D(f_hist, r_hist):
    c = ROOT.TCanvas('c', 'Pull')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
    ROOT.gStyle.SetNumberContours(255)

    chi2 = 0
    nBins = 0
    pull_hist = r_hist.Clone("pull_hist")
    pull_hist.Reset()

    # DEBUG
    skip = 0
    overflow = 0

    # Normalize f_hist
    f_hist.Scale(r_hist.GetEntries()/f_hist.GetEntries())

    for x in range(1, r_hist.GetNbinsX()+1):
        for y in range(1, r_hist.GetNbinsY()+1):

            # Bin 1 data
            bin1 = f_hist.GetBinContent(x, y)
            bin1err = f_hist.GetBinError(x, y)

            # Bin 2 data
            bin2 = r_hist.GetBinContent(x, y)
            bin2err = r_hist.GetBinError(x, y)

            nBins += 1
            if bin1err == 0 and bin2err == 0:
                skip += 1
                continue

            new_pull = pull(bin1, bin1err, bin2, bin2err)

            # Sum pulls
            chi2 += new_pull**2

            # Fill Pull Histogram
            if new_pull > 50:
                overflow += 1
                new_pull = 50
            if new_pull < -50:
                overflow += 1
                new_pull = -50

            pull_hist.SetBinContent(x, y, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    # Plot pull hist
    pull_hist.GetZaxis().SetRangeUser(-50, 50)
    pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
    pull_hist.Draw("colz")

    # DEBUG
    # print("X Bins: {0}".format(r_hist.GetNbinsX()))
    # print("Y Bins: {0}".format(r_hist.GetNbinsY()))
    # print("Total bins: {0}".format(nBins))
    # print("Skipped: {0}".format(skip))
    # print("Capped data: {0}".format(overflow))
    # print("Chi2: {0}".format(chi2))

    return chi2

# End Parsing Functions ------

# Analysis Functions ------
def pull(bin1, binerr1, bin2, binerr2):

    '''
        pull = [(data - expected)^2]/(sum of errors in quadrature)
        data = |bin1 - bin2|, expected = 0

    '''

    pull = ((bin1 - bin2))/((binerr1**2 + binerr2**2)**(0.5))

    return pull

# End Analysis Functions

# AutoDQM
def auto_dqm():

    # Ensure no graphs are drawn to screen
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    # Set up canvas for chi2 plot
    C = ROOT.TCanvas('C', 'Chi2')

    # Location of root files
    # tfiles_dir = "/nfs-6/userdata/bemarsh/CSC_DQM/Run2017/SingleMuon/"
    # tfiles = os.listdir(tfiles_dir)
    tfiles_dir = "/home/users/jguiang/projects/AutoDQM/test_files/"
    tfiles = os.listdir(tfiles_dir)

    # Main dir = location of plots, sub dir = sub-directories we are interested in
    main_dir = "DQMData/Run {0}/CSC/Run summary/CSCOfflineMonitor/"
    sub_dirs = ["Occupancy/", "recHits/"]

    # Reference file run number
    r_num = "301531"

    # Remove reference file from tfiles
    if r_num in tfiles:
        tfiles.remove(r_num+".root")

    # Chi2 Plot
    chi2_hist = ROOT.TH1F("chi2", "#Chi^{2}", 20, 0, 100)

    # Parse root files
    for tfile in tfiles:
        print "File: {0}".format(tfile)

        # Parse desired sub-directories
        for sub_dir in sub_dirs:
            hists = ROOT.TFile.Open(tfiles_dir+r_num+".root")
            keys = hists.GetDirectory("{0}{1}".format(main_dir.format(r_num), sub_dir))
            histograms = {}

            # Populate histogram map
            for key in keys.GetListOfKeys():
                histograms[key.GetName()] = key.ReadObj()

            # Parse histograms
            for hist_name in histograms:
                f_num = tfile.split(".")[0]

                # Open DQM root file
                new_file = ROOT.TFile.Open(tfiles_dir+tfile)

                # Open reference file
                new_ref = ROOT.TFile.Open(tfiles_dir+r_num+".root")


                # Open recHits
                f_path = "{0}{1}{2}".format(main_dir.format(f_num), sub_dir, hist_name)
                r_path = "{0}{1}{2}".format(main_dir.format(r_num), sub_dir, hist_name)
                # print("New File: "+f_path)
                f_hist = new_file.Get(f_path)

                # print("Reference: "+r_path)
                r_hist = new_ref.Get(r_path)

                if "TH1" in str(histograms[hist_name]):
                    chi2_hist.Fill(scan_1D(f_hist, r_hist))
                elif "TH2" in str(histograms[hist_name]):
                    chi2_hist.Fill(scan_2D(f_hist, r_hist))
                else:
                    print(histograms[hist_name])

    chi2_hist.GetXaxis().SetTitle("#Chi^{2}")
    chi2_hist.GetYaxis().SetTitle("Entries")
    chi2_hist.Draw("hist")
    C.SaveAs("tests/test1.pdf")


if __name__ == "__main__":
    auto_dqm()
