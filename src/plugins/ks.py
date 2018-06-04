#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT

def comparators():
    return {
        "ks_test": ks
    }


def ks(histpair, ks_cut=0.09, min_entries=100000, **kwargs):

    data_name = histpair.data_name
    ref_name = histpair.ref_name
    
    data_hist = histpair.data_hist
    ref_hist = histpair.ref_hist

    # Normalize data_hist
    if data_hist.GetEntries() > 0:
        data_hist.Scale(ref_hist.GetEntries() / data_hist.GetEntries())

    # Reject empty histograms
    is_good = data_hist.GetEntries() != 0 and data_hist.GetEntries() >= min_entries

    ks = data_hist.KolmogorovTest(ref_hist, "M")

    is_outlier = is_good and ks > ks_cut

    canv = draw_same(ref_hist, data_hist)

    info = {
        'Data_Entries': data_hist.GetEntries(),
        'Ref_Entries': ref_hist.GetEntries(),
        'KS_Val': ks
    }
    return canv, is_outlier, info


def draw_same(ref_hist, data_hist):
    # Set up canvas
    c = ROOT.TCanvas('c', 'c')

    # Ensure plot accounts for maximum value
    ref_hist.SetMaximum(max(data_hist.GetMaximum(), ref_hist.GetMaximum()) * 1.1)

    ROOT.gStyle.SetOptStat(1)
    ref_hist.SetStats(True)
    data_hist.SetStats(True)

    # Set hist style
    ref_hist.SetLineColor(28)
    ref_hist.SetFillColor(20)
    ref_hist.SetLineWidth(1)
    data_hist.SetLineColor(ROOT.kRed)
    data_hist.SetLineWidth(1)

    # Plot hist
    ref_hist.Draw()
    data_hist.Draw("sames hist e")

    # Draw stats boxes
    ref_hist.SetName("Reference")
    data_hist.SetName("Data")

    r_stats = ref_hist.FindObject("stats")
    f_stats = data_hist.FindObject("stats")

    r_stats.SetY1NDC(0.15)
    r_stats.SetY2NDC(0.30)
    r_stats.SetTextColor(28)
    r_stats.Draw()

    f_stats.SetY1NDC(0.35)
    f_stats.SetY2NDC(0.50)
    f_stats.SetTextColor(ROOT.kRed)
    f_stats.Draw()

    # Text box
    data_text = ROOT.TLatex(.52, .91, "#scale[0.6]{Data: " + data_name + "}")
    ref_text = ROOT.TLatex(.72, .91, "#scale[0.6]{Ref: " + ref_name + "}")
    data_text.SetNDC(ROOT.kTRUE)
    ref_text.SetNDC(ROOT.kTRUE)
    data_text.Draw()
    ref_text.Draw()

    return c
