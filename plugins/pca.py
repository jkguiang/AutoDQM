import os,sys,json
import cPickle as pickle
import numpy as np
from sklearn.decomposition import PCA
import ROOT
ROOT.gROOT.SetBatch(1)
import utils

from autodqm.plugin_results import PluginResults

def comparators():
    return {
        'pca': pca        
    }

def pca(histpair,
        sse_percentile=5, exp_var=0.95, norm_type='all', min_entries=100000,
        **kwargs):

    data_name = histpair.data_name
    data_hist = histpair.data_hist

    # Check for unique Pickle file
    possible_pickles = glob.glob("pickle_jar/*_{}.pkl".format(data_name))
    if len(possible_pickles) != 1: return None

    # Load Pickle file
    pca_dict = pickle.load(open(possible_pickles[0], "rb"))

    # Check that the hist is a histogram
    if not data_hist.InheritsFrom('TH1'):
        return None

    # Normalize data_hist
    if data_hist.GetEntries() > 0:
        data_hist.Scale(1.0 / data_hist.Integral())

    # Reject empty histograms
    is_good = data_hist.GetEntries() != 0 and data_hist.GetEntries() >= min_entries

    np_data = get_np_data(data_hist)
    # Get 'good' (non-zero) bins
    np_data = np_data[pca_dict["good_bins"]]

    n_components = get_components(exp_var, pca_dict["pca"].explained_variance_ratio_)
    sse, reco_data = PCATest(np_data, pca_dict["pca"], n_components)

    c, artifacts = draw_same(data_hist, reco_data, pca_dict["good_bins"], histpair.data_run)

    # Get SSE cut
    sse_cut = pca_dict["sses_{}comp".format(n_components)]["{}pct".format(sse_percentile)]

    outlier = is_good and sse > sse_cut

    info = {
        'Data_Entries': data_hist.GetEntries(),
        'Sum of Squared Errors': sse,
        'PCA Components': n_components
    }

    return PluginResults(
            c,
            show=is_outlier,
            info=info,
            artifacts=artifacts)

def PCATest(np_data, pca_obj, n_components):

    # Transform data in terms of principle component vectors
    transform = pca.transform(np_data)
    # Zero out components beyond n_components cap
    transform[n_components:] *= 0
    # Reconstruct data using N components
    reco_data = pca.inv_transform(transform)
    # Get sum of squared errors
    sse = np.sqrt(np.sum((reco_data - np_data)**2))

    return sse, reco_data

def get_components(exp_var, exp_var_ratios_, n_cap=3):

    sum_var = 0
    n_components = 0
    for var_ratio in exp_var_ratios_:
        n_components += 1
        sum_var += var_ratio
        if sum_var >= exp_var or n_components >= n_cap:
            return n_components 

    return n_components

def get_np_data(data_hist):
    np_data = []
    for x in range(1, data_hist.GetNbinsX() +1):
        np_data.append(data_hist.GetBinContent(x))

    return np.array(np_data)

def draw_same(data_hist, reco_data, reco_bins, data_run):
    # Set up canvas
    c = ROOT.TCanvas('c', 'c')
    data_hist = data_hist.Clone()
    reco_hist = data_hist.Clone("reco_hist")
    reco_hist.Reset()
    
    # Fill Reco hist
    for i in range(0, len(reco_bins)):
        reco_hist.SetBinContent(reco_bins[i], reco_data[i])

    ROOT.gStyle.SetOptStat(1)
    data_hist.SetStats(True)
    reco_hist.SetStats(True)

    # Set hist style
    data_hist.SetLineColor(ROOT.kBlue)
    data_hist.SetLineWidth(1)
    reco_hist.SetLineColor(ROOT.kGreen)
    reco_hist.SetLineStyle(7)
    reco_hist.SetLineWidth(1)

    # Name histograms
    data_hist.SetName("Data")
    reco_hist.SetName("Reconstructed")

    # Plot hist
    data_hist.Draw()
    reco_hist.Draw("same")
    c.Update()

    # Modify stats boxes
    d_stats = data_hist.FindObject("stats")
    r_stats = reco_hist.FindObject("stats")

    d_stats.SetY1NDC(0.15)
    d_stats.SetY2NDC(0.30)
    d_stats.SetTextColor(ROOT.kBlue)
    d_stats.Draw()

    r_stats.SetY1NDC(0.35)
    r_stats.SetY2NDC(0.50)
    r_stats.SetTextColor(ROOT.kGreen)
    r_stats.Draw()

    # Text box
    data_text = ROOT.TLatex(.72, .91, "#scale[0.6]{Data: " + data_run + "}")
    data_text.SetNDC(ROOT.kTRUE)
    data_text.Draw()

    c.Update()
    artifacts = [data_hist, reco_hist, data_text]
    return c, artifacts
