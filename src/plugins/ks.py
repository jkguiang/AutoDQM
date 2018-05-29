#!/usr/bin/env python
# -*- coding: utf-8 -*-


def comparators():
    return {
        "ks_test": ks
    }


def ks(histpair, ks_cut=0.09, min_entries=100000, **kwargs):

    r_hist = histpair.ref
    f_hist = histpair.data

    # Normalize f_hist
    if f_hist.GetEntries() > 0:
        f_hist.Scale(r_hist.GetEntries() / f_hist.GetEntries())

    # Reject empty histograms
    is_good = f_hist.GetEntries() != 0 and f_hist.GetEntries() >= min_entries

    ks = f_hist.KolmogorovTest(r_hist, "M")

    is_outlier = is_good and ks > ks_cut

    canv = draw_same(r_hist, f_hist)

    info = {
        'Data_Entries': f_hist.GetEntries(),
        'Ref_Entries': r_hist.GetEntries(),
        'KS_Val': ks
    }
    return canv, is_outlier, info


def draw_same(r_hist, f_hist):
    # Set up canvas
    c = ROOT.TCanvas('c', 'c')

    # Ensure plot accounts for maximum value
    r_hist.SetMaximum(max(f_hist.GetMaximum(), r_hist.GetMaximum()) * 1.1)

    ROOT.gStyle.SetOptStat(1)
    r_hist.SetStats(True)
    f_hist.SetStats(True)

    # Set hist style
    r_hist.SetLineColor(28)
    r_hist.SetFillColor(20)
    r_hist.SetLineWidth(1)
    f_hist.SetLineColor(ROOT.kRed)
    f_hist.SetLineWidth(1)

    # Plot hist
    r_hist.Draw()
    f_hist.Draw("sames hist e")

    # Draw stats boxes
    r_hist.SetName("Reference")
    f_hist.SetName("Data")

    r_stats = r_hist.FindObject("stats")
    f_stats = f_hist.FindObject("stats")

    r_stats.SetY1NDC(0.15)
    r_stats.SetY2NDC(0.30)
    r_stats.SetTextColor(28)
    r_stats.Draw()

    f_stats.SetY1NDC(0.35)
    f_stats.SetY2NDC(0.50)
    f_stats.SetTextColor(ROOT.kRed)
    f_stats.Draw()

    # Text box
    data_text = ROOT.TLatex(.52, .91, "#scale[0.6]{Data: " + data_id + "}")
    ref_text = ROOT.TLatex(.72, .91, "#scale[0.6]{Ref: " + ref_id + "}")
    data_text.SetNDC(ROOT.kTRUE)
    ref_text.SetNDC(ROOT.kTRUE)
    data_text.Draw()
    ref_text.Draw()

    return c
