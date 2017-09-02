import ROOT
import os
import sys

# Parsing Functions -------

# Scan 1D Hist, plot Pull hist and compute Chi^2
def scan_1D(f_hist, r_hist, hist, f_num, targ_dir):
    c = ROOT.TCanvas('c', 'Pull')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
    ROOT.gStyle.SetNumberContours(255)

    is_good = True
    chi2 = 0
    is_outlier = False
    max_pull = 0
    nBins = 0
    pull_hist = r_hist.Clone("pull_hist")
    pull_hist.Reset()

    if f_hist.GetEntries() == 0:
        is_good = False
        return is_good, chi2, max_pull, is_outlier

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

        # Check for max pull
        if new_pull > max_pull:
            max_pull = new_pull

        # Fill Pull Histogram
        pull_hist.SetBinContent(x, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    if chi2 > 80:

        # Plot pull hist
        pull_hist.SetFillColor(ROOT.kGreen)
        pull_hist.SetLineColor(ROOT.kBlack)
        pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
        pull_hist.Draw("hist")

        # Text box
        text = ROOT.TLatex(0,.9,"#scale[0.6]{Run: "+f_num+"}");  
        text.SetNDC(ROOT.kTRUE);
        text.Draw()

        is_outlier = True
        c.SaveAs("{0}/{1}_{2}.pdf".format(targ_dir, hist, f_num))

    # DEBUG
    # print("Chi2: {0}".format(chi2))

    return chi2, max_pull, is_outlier

# Scan 2D Hist, plot Pull hist and compute Chi^2
def scan_2D(f_hist, r_hist, hist, f_num, targ_dir):
    c = ROOT.TCanvas('c', 'Pull')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
    ROOT.gStyle.SetNumberContours(255)

    is_good = True
    chi2 = 0
    is_outlier = False
    max_pull = 0
    nBins = 0
    pull_hist = r_hist.Clone("pull_hist")
    pull_hist.Reset()

    # DEBUG
    skip = 0
    overflow = 0

    if f_hist.GetEntries() == 0:
        is_good = False
        return is_good, chi2, max_pull, is_outlier

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

            # Check if max_pull
            if new_pull > max_pull:
                max_pull = new_pull

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

    if chi2 > 50:

        # Plot pull hist
        pull_hist.GetZaxis().SetRangeUser(-50, 50)
        pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
        pull_hist.Draw("colz")

        # Text box
        text = ROOT.TLatex(.79,.91,"#scale[0.6]{Run: "+f_num+"}");  
        text.SetNDC(ROOT.kTRUE);
        text.Draw()

        is_outlier = True
        c.SaveAs("{0}/{1}_{2}.pdf".format(targ_dir, hist, f_num))

        # Write text file
        new_txt = open("{0}/{1}_{2}.txt".format(targ_dir.split("pdfs")[0]+"txts" , hist, f_num), "w")
        new_txt.writelines(["Run: {0}\n".format(f_num), 
                            "Max Pull Value: {0}\n".format(max_pull),
                            "Chi^2: {0}\n".format(chi2)])
        new_txt.close()

    return is_good, chi2, max_pull, is_outlier

# End Parsing Functions ------

# Analysis Functions ------
def pull(bin1, binerr1, bin2, binerr2):

    '''
        pull = [(data - expected)^2]/(sum of errors in quadrature)
        data = |bin1 - bin2|, expected = 0

    '''

    pull = ((bin1 - bin2))/((binerr1**2 + binerr2**2)**(0.5))

    return pull

# End Analysis Functions ------

# AutoDQM
def auto_dqm():

    targ_dir = "/home/users/jguiang/public_html/dqm/pdfs"

    # Check to make sure output directory exists
    if not os.path.isdir(targ_dir):
        print("Target directory path does not exist or is not a directory.")
        return

    # Ensure no graphs are drawn to screen and no root messages are sent to terminal
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    # Set up canvas for chi2 plot
    C = ROOT.TCanvas('C', 'Chi2')

    # Location of root files
    tfiles_dir = "/nfs-6/userdata/bemarsh/CSC_DQM/Run2017/SingleMuon/"
    tfiles = os.listdir(tfiles_dir)
    total_tfiles = (len(os.listdir(tfiles_dir)) - 1)
    # tfiles_dir = "/home/users/jguiang/projects/AutoDQM/test_files/"
    # tfiles = os.listdir(tfiles_dir)

    # Main dir = location of plots
    main_dir = "DQMData/Run {0}/CSC/Run summary/CSCOfflineMonitor/"

    # Reference file run number
    r_num = "301531"

    # Remove reference file from tfiles
    tfiles.remove(r_num+".root")

    # Chi2 Plot
    chi2_1D = ROOT.TH1F("chi2_1D", "#Chi^{2} for 1D Histograms", 20, 0, 100)
    chi2_2D = ROOT.TH1F("chi2_2D", "#Chi^{2} for 2D Histograms", 20, 0, 100)

    # PARSE SPECIFIC HISTOGRAM ------------
    hist = "hORecHits"
    sub_dir = "Occupancy/"
    # Parse root files
    files = 0
    outliers = 0
    for tfile in tfiles:
        # print "File: {0}".format(tfile)
        files += 1

        f_num = tfile.split(".")[0]

        # Open DQM root file
        new_file = ROOT.TFile.Open(tfiles_dir+tfile)

        # Open reference file
        new_ref = ROOT.TFile.Open(tfiles_dir+r_num+".root")

        # Open recHits
        f_path = "{0}{1}{2}".format(main_dir.format(f_num), sub_dir, hist)
        r_path = "{0}{1}{2}".format(main_dir.format(r_num), sub_dir, hist)
        # print("New File: "+f_path)
        f_hist = new_file.Get(f_path)

        # print("Reference: "+r_path)
        r_hist = new_ref.Get(r_path)

        if type(f_hist) == ROOT.TH1F:
            is_good, chi2, max_pull, is_outlier = scan_1D(f_hist, r_hist, hist, f_num, targ_dir)
            if is_good:
                chi2_1D.Fill(chi2)
            if is_outlier:
                outliers += 1
        elif type(f_hist) == ROOT.TH2F:
            is_good, chi2, max_pull, is_outlier = scan_2D(f_hist, r_hist, hist, f_num, targ_dir)
            if is_good:
                chi2_2D.Fill(chi2)
            if is_outlier:
                outliers += 1
        else:
            print("Not a histogram: {0}".format(hist))

        # Update Terminal
        sys.stdout.write("\r")
        sys.stdout.write("Files: {0}/{1}    Outliers: {2}".format(files, total_tfiles, outliers)) 
        sys.stdout.flush()

    # PARSE ALL HISTOGRAMS ------------
    # sub_dirs = ["Occupancy/"]
    # Parse root files
    # for tfile in tfiles:
    #     print "File: {0}".format(tfile)

    #     # Parse desired sub-directories
    #     for sub_dir in sub_dirs:
    #         hists = ROOT.TFile.Open(tfiles_dir+r_num+".root")
    #         keys = hists.GetDirectory("{0}{1}".format(main_dir.format(r_num), sub_dir))
    #         histograms = {}

    #         # Populate histogram map
    #         for key in keys.GetListOfKeys():
    #             histograms[key.GetName()] = key.ReadObj()

    #         # Parse histograms
    #         for hist in histograms:
    #             f_num = tfile.split(".")[0]

    #             # Open DQM root file
    #             new_file = ROOT.TFile.Open(tfiles_dir+tfile)

    #             # Open reference file
    #             new_ref = ROOT.TFile.Open(tfiles_dir+r_num+".root")


    #             # Open recHits
    #             f_path = "{0}{1}{2}".format(main_dir.format(f_num), sub_dir, hist)
    #             r_path = "{0}{1}{2}".format(main_dir.format(r_num), sub_dir, hist)
    #             # print("New File: "+f_path)
    #             f_hist = new_file.Get(f_path)

    #             # print("Reference: "+r_path)
    #             r_hist = new_ref.Get(r_path)

    #             if "TH1" in str(histograms[hist]):
    #                 chi2_1D.Fill(scan_1D(f_hist, r_hist, hist, f_num))
    #             elif "TH2" in str(histograms[hist]):
    #                 chi2_2D.Fill(scan_2D(f_hist, r_hist, hist, f_num))
    #             else:
    #                 print(histograms[hist])

    chi2_1D.GetXaxis().SetTitle("#Chi^{2}")
    chi2_1D.GetYaxis().SetTitle("Entries")
    chi2_2D.GetXaxis().SetTitle("#Chi^{2}")
    chi2_2D.GetYaxis().SetTitle("Entries")
    chi2_1D.Draw("hist")

    C.SaveAs("{0}/chi2_1D.pdf".format(targ_dir))
    chi2_2D.Draw("hist")
    C.SaveAs("{0}/chi2_2D.pdf".format(targ_dir))

    print("\rFiles: {0}/{1}    Outliers: {2}\n".format(files, total_tfiles, outliers))

if __name__ == "__main__":
    auto_dqm()
