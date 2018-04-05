#!/usr/bin/env python
# -*- coding: utf-8 -*-


class HistPair(object):

    """ Data class for storing data and ref histograms to be compared by AutoDQM, as well as any relevant configuration parameters. """

    def __init__(self, dataHist, refHist, config):
        self.data = dataHist
        self.ref = refHist

        self.name_out = config.get("name_out", dataHist.GetName())
        self.chi2_cut = config.get("chi2_cut", 500)
        self.pull_cap = config.get("pull_cap", 25)
        self.pull_cut = config.get("pull_cut", 20)
        self.ks_cut = config.get("ks_cut", 0.09)
        self.min_entries = config.get("min_entries", 100000)
        self.always_draw = config.get("always_draw", False)
        self.norm_type = config.get("norm_type", 'all')
