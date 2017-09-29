import ROOT
import os
import sys

# Parsing Functions -------

# Scan 1D Hist, plot Pull hist and compute Chi^2
def scan_1D(f_hist, r_hist, name, f_id, targ_dir):
    # Set up canvas
    c = ROOT.TCanvas('c', 'Pull')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
    ROOT.gStyle.SetNumberContours(255)

    # Variable declarations
    is_good = True
    chi2 = 0
    is_outlier = False
    max_pull = 0
    nBins = 0
    
    # Get empty clone of reference histogram for pull hist
    pull_hist = r_hist.Clone("pull_hist")
    pull_hist.Reset()

    # Reject empty histograms
    if f_hist.GetEntries() == 0 or f_hist.GetEntries() < 100000:
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

        # Count bins for chi2 calculation
        nBins += 1

        # Ensure that divide-by-zero error is not thrown when calculating pull
        if bin1err == 0 and bin2err == 0:
            continue

        # Calculate pull
        new_pull = pull(bin1, bin1err, bin2, bin2err)

        # Sum pulls
        chi2 += new_pull**2

        # Check if max_pull
        if abs(new_pull) > abs(max_pull):
            max_pull = new_pull

        # Cap pull values displayed on histogram (max pull calculated before this)
        if new_pull > 100:
            new_pull = 100
        if new_pull < -100:
            new_pull = -100

        # Fill Pull Histogram
        pull_hist.SetBinContent(x, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    # Chi2 Cut
    if chi2 > 50:
        # Used in outliers count
        is_outlier = True

        # Plot pull hist
        pull_hist.GetZaxis().SetRangeUser(-50, 50)
        pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
        pull_hist.Draw("colz")

        # Text box
        text = ROOT.TLatex(.79,.91,"#scale[0.6]{Run: "+f_id+"}") 
        text.SetNDC(ROOT.kTRUE);
        text.Draw()

        c.SaveAs("{0}/pdfs/{1}_{2}.pdf".format(targ_dir, name, f_id))

        # Write text file
        new_txt = open("{0}/txts/{1}_{2}.txt".format(targ_dir, name, f_id), "w")
        new_txt.writelines(["Run: {0}\n".format(f_id), 
                            "Max Pull Value: {0}\n".format(max_pull),
                            "Chi^2: {0}\n".format(chi2),
                            "Entries: {0}\n".format(int(f_hist.GetEntries()))])
        new_txt.close()

    return is_good, chi2, max_pull, is_outlier

# Scan 2D Hist, plot Pull hist and compute Chi^2
def scan_2D(f_hist, r_hist, name, f_id, targ_dir):
    # Set up canvas
    c = ROOT.TCanvas('c', 'Pull')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
    ROOT.gStyle.SetNumberContours(255)

    # Variable declarations
    is_good = True
    chi2 = 0
    is_outlier = False
    max_pull = 0
    nBins = 0
    
    # Get empty clone of reference histogram for pull hist
    pull_hist = r_hist.Clone("pull_hist")
    pull_hist.Reset()

    # Reject empty histograms
    if f_hist.GetEntries() == 0 or f_hist.GetEntries() < 100000:
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

            # Count bins for chi2 calculation
            nBins += 1

            # Ensure that divide-by-zero error is not thrown when calculating pull
            if bin1err == 0 and bin2err == 0:
                continue

            # Calculate pull
            new_pull = pull(bin1, bin1err, bin2, bin2err)

            # Sum pulls
            chi2 += new_pull**2

            # Check if max_pull
            if abs(new_pull) > abs(max_pull):
                max_pull = new_pull

            # Cap pull values displayed on histogram (max pull calculated before this)
            if new_pull > 50:
                new_pull = 50
            if new_pull < -50:
                new_pull = -50

            # Fill Pull Histogram
            pull_hist.SetBinContent(x, y, new_pull)

    # Compute chi2
    chi2 = (chi2/nBins)

    # Chi2 Cut
    if chi2 > 500 or abs(max_pull) > 40:
        # Used in outliers count
        is_outlier = True

        # Plot pull hist
        pull_hist.GetZaxis().SetRangeUser(-50, 50)
        pull_hist.SetTitle(pull_hist.GetTitle()+" Pull Values")
        pull_hist.Draw("colz")

        # Text box
        text = ROOT.TLatex(.79,.91,"#scale[0.6]{Run: "+f_id+"}") 
        text.SetNDC(ROOT.kTRUE);
        text.Draw()

        c.SaveAs("{0}/pdfs/{1}_{2}.pdf".format(targ_dir, name, f_id))

        # Write text file
        new_txt = open("{0}/txts/{1}_{2}.txt".format(targ_dir, name, f_id), "w")
        new_txt.writelines(["Run: {0}\n".format(f_id), 
                            "Max Pull Value: {0}\n".format(max_pull),
                            "Chi^2: {0}\n".format(chi2),
                            "Entries: {0}\n".format(int(f_hist.GetEntries()))])
        new_txt.close()

    return is_good, chi2, max_pull, is_outlier

# End Parsing Functions ------

# Comparison Plots ------

def draw_same(f_hist, r_hist, name, f_id, targ_dir):
    # Plots that should always be drawn
    hists = ["hSnhits", "hSnSegments", "hWirenGroupsTotal", "hStripNFired", "hRHnrechits"]

    # Set up canvas
    c = ROOT.TCanvas('c', 'c')

    # Variable declarations
    is_good = True
    chi2 = 0
    is_outlier = False
    max_pull = 0
    nBins = 0
    
    # Reject empty histograms
    if f_hist.GetEntries() == 0 or f_hist.GetEntries() < 100000:
        if name not in hists:
            is_good = False
            return is_good, chi2, max_pull, is_outlier

    # Normalize f_hist
    f_hist.Scale(r_hist.GetEntries()/f_hist.GetEntries())

    # Ensure plot accounts for maximum value
    r_hist.SetMaximum(max(f_hist.GetMaximum(), r_hist.GetMaximum()))

    for x in range(1, r_hist.GetNbinsX()+1):

        # Bin 1 data
        bin1 = f_hist.GetBinContent(x)
        bin1err = f_hist.GetBinError(x)

        # Bin 2 data
        bin2 = r_hist.GetBinContent(x)
        bin2err = r_hist.GetBinError(x)

        # Count bins for chi2 calculation
        nBins += 1

        # Ensure that divide-by-zero error is not thrown when calculating pull
        if bin1err == 0 and bin2err == 0:
            continue

        # Calculate pull
        new_pull = pull(bin1, bin1err, bin2, bin2err)

        # Sum pulls
        chi2 += new_pull**2

        # Check if max_pull
        if abs(new_pull) > abs(max_pull):
            max_pull = new_pull

        # Cap pull values displayed on histogram (max pull calculated before this)
        if new_pull > 100:
            new_pull = 100
        if new_pull < -100:
            new_pull = -100

    # Compute chi2
    chi2 = (chi2/nBins)

    # Chi2 Cut
    if chi2 > 500 or abs(max_pull) > 40 or name in hists:
        # Used in outliers count
        is_outlier = True

        # Stat boxes only for names in hists
        if name in hists:
            ROOT.gStyle.SetOptStat(1)
        else:
            ROOT.gStyle.SetOptStat(0)

        # Set hist style
        r_hist.SetLineColor(28)
        r_hist.SetFillColor(20)
        r_hist.SetLineWidth(2)
        f_hist.SetLineColor(ROOT.kBlack)
        f_hist.SetLineWidth(2)

        # Plot hist
        r_hist.Draw()
        f_hist.Draw("sames")

        if name in hists:
            # Draw stats boxes
            r_hist.SetName("Reference")
            f_hist.SetName("Data")
            c.Update()

            r_stats = r_hist.FindObject("stats")
            f_stats = f_hist.FindObject("stats")

            r_stats.SetY1NDC(0.15)
            r_stats.SetY2NDC(0.30)
            r_stats.SetTextColor(28)
            r_stats.Draw()

            f_stats.SetY1NDC(0.35)
            f_stats.SetY2NDC(0.50)
            f_stats.Draw()

        # Text box
        text = ROOT.TLatex(.15,.91,"#scale[0.6]{Run: "+f_id+"}") 
        text.SetNDC(ROOT.kTRUE);
        text.Draw()

        c.SaveAs("{0}/pdfs/{1}_{2}.pdf".format(targ_dir, name, f_id))

        # Write text file
        new_txt = open("{0}/txts/{1}_{2}.txt".format(targ_dir, name, f_id), "w")
        new_txt.writelines(["Run: {0}\n".format(f_id), 
                            "Max Pull Value: {0}\n".format(max_pull),
                            "Chi^2: {0}\n".format(chi2),
                            "Entries: {0}\n".format(int(f_hist.GetEntries()))])
        new_txt.close()

    return is_good, chi2, max_pull, is_outlier

# End Comparison Plots

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
def autodqm(f_hists, r_hists, f_id, targ_dir):
    # Ensure no graphs are drawn to screen and no root messages are sent to terminal
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    max_1D = 0
    max_2D = 0

    C = ROOT.TCanvas("C", "Chi2")
    chi2_1D = ROOT.TH1F("chi2_1D", "#Chi^{2} for 1D Histograms", 60, 0, 300)
    chi2_2D = ROOT.TH1F("chi2_2D", "#Chi^{2} for 2D Histograms", 60, 0, 300)

    outliers = 0

    for name in f_hists:
        if not (name in r_hists): continue
        if type(f_hists[name]) != type(r_hists[name]): continue

        if type(f_hists[name]) == ROOT.TH1F:
            is_good, chi2, max_pull, is_outlier = draw_same(f_hists[name], r_hists[name], name, f_id, targ_dir)
            if is_good:
                chi2_1D.Fill(chi2)
                if chi2 > max_1D:
                    max_1D = chi2
            if is_outlier:
                outliers += 1
        elif type(f_hists[name]) == ROOT.TH2F:
            is_good, chi2, max_pull, is_outlier = scan_2D(f_hists[name], r_hists[name], name, f_id, targ_dir)
            if is_good:
                chi2_2D.Fill(chi2)
                if chi2 > max_2D:
                    max_2D = chi2
            if is_outlier:
                outliers += 1

        else:
            skip += 1

    chi2_1D.GetXaxis().SetTitle("#Chi^{2}")
    chi2_1D.GetYaxis().SetTitle("Entries")

    chi2_1D.GetXaxis().SetRangeUser(0, int(max_1D))
    chi2_1D.GetXaxis().SetLimits(0, max_1D)

    chi2_1D.Draw("hist")
    C.SaveAs("{0}/pdfs/chi2_1D.pdf".format(targ_dir))

    chi2_2D.GetXaxis().SetTitle("#Chi^{2}")
    chi2_2D.GetYaxis().SetTitle("Entries")

    # chi2_2D.GetXaxis().SetRangeUser(0, int(max_2D))
    # chi2_2D.GetXaxis().SetLimits(0, max_2D)

    chi2_2D.Draw("hist")
    C.SaveAs("{0}/pdfs/chi2_2D.pdf".format(targ_dir))

    return

if __name__ == "__main__":

    # targ_dir = "/home/users/jguiang/public_html/dqm/pdfs"

    # # Location of root files
    # tfiles_dir = "/nfs-6/userdata/bemarsh/CSC_DQM/Run2017/SingleMuon/"
    # tfiles = os.listdir(tfiles_dir)
    # total_tfiles = (len(os.listdir(tfiles_dir)) - 1)
    # # tfiles_dir = "/home/users/jguiang/projects/AutoDQM/test_files/"
    # # tfiles = os.listdir(tfiles_dir)

    # # Main dir = location of plots
    # main_dir = "DQMData/Run {0}/CSC/Run summary/CSCOfflineMonitor/"

    # # Reference file run number
    # r_num = "301531"

    targ_dir = "/home/users/jguiang/public_html/dqm_test/pdfs"

    # Location of root files
    tfiles_dir = "root_files/"

    # Reference file run number
    r_num = "301531"

    auto_dqm(targ_dir, tfiles_dir, r_num)
