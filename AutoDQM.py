import ROOT

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
        pull_hist.Fill(x, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    # Plot pull hist
    pull_hist.SetFillColor(ROOT.kGreen)
    pull_hist.SetLineColor(ROOT.kBlack)
    pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
    pull_hist.Draw("hist")

    # DEBUG
    print("Chi2: {0}".format(chi2))

    while True:
        inp = raw_input("(DEBUG) type '.q' to quit: ")
        if inp == ".q":
            break
    return

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

    # Normalize f_hist
    f_hist.Scale(r_hist.GetEntries()/f_hist.GetEntries())

    for x in range(1, r_hist.GetNbinsX()+1):
        for y in range(1, r_hist.GetNbinsY()+1):

            # Bin 1 data
            bin1_coord = f_hist.GetBin(x, y)
            bin1 = f_hist.GetBinContent(bin1_coord)
            bin1err = f_hist.GetBinError(bin1_coord)

            # Bin 2 data
            bin2_coord = r_hist.GetBin(x, y)
            bin2 = r_hist.GetBinContent(bin2_coord)
            bin2err = r_hist.GetBinError(bin2_coord)

            nBins += 1
            if bin1err == 0 and bin2err == 0:
                continue

            new_pull = pull(bin1, bin1err, bin2, bin2err)

            # Sum pulls
            chi2 += new_pull**2

            # Fill Pull Histogram
            if new_pull > 50:
                new_pull = 50
            if new_pull < -50:
                new_pull = -50

            pull_hist.Fill(x, y, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    # Plot pull hist
    pull_hist.GetZaxis().SetRangeUser(-50, 50)
    pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
    pull_hist.Draw("colz")

    # DEBUG
    print("Chi2: {0}".format(chi2))

    while True:
        inp = raw_input("(DEBUG) type '.q' to quit: ")
        if inp == ".q":
            break
    return

# End Parsing Functions ------

# Analysis Functions ------
def pull(bin1, binerr1, bin2, binerr2):

    # pull = [(data - expected)^2]/(sum of errors in quadrature)
    # data = |bin1 - bin2|, expected = 0

    pull = ((bin1 - bin2))/((binerr1**2 + binerr2**2)**(0.5))

    return pull

# End Analysis Functions

# AutoDQM
def auto_dqm():
    main_dir = "DQMData/Run {0}/CSC/Run summary/CSCOfflineMonitor/"
    sub_dir = ["Occupancy/", "recHits/"]
    file_num = "300816"
    ref_num = "301531"

    hist_name = "hORecHitSerial"

    # Open DQM root file
    new_file = ROOT.TFile.Open(file_num+".root")

    # Open reference file
    new_ref = ROOT.TFile.Open(ref_num+".root")


    # Open recHits
    print("New File: {0}{1}{2}".format(main_dir.format(file_num), sub_dir[0], hist_name))
    f_hist = new_file.Get("{0}{1}{2}".format(main_dir.format(file_num), sub_dir[0], hist_name))

    print("Reference: {0}{1}{2}".format(main_dir.format(ref_num), sub_dir[0], hist_name))
    r_hist = new_ref.Get("{0}{1}{2}".format(main_dir.format(ref_num), sub_dir[0], hist_name))

    scan_1D(f_hist, r_hist)

if __name__ == "__main__":
    auto_dqm()
    # while True:
    #     inp = raw_input("(DEBUG) type '.q' to quit: ")
    #     if inp == ".q":
    #         break
