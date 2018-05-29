#!/usr/bin/env python2
# -*- coding: utf-8 -*-


class HistPair(object):
    """Data class for storing data and ref histograms to be compared by AutoDQM, as well as any relevant configuration parameters."""

    def __init__(self, dataHist, refHist, config):

        self.data = dataHist
        self.ref = refHist

        self.config = config
        self.comparators = config.get(
            'comparators', ('pull_values', 'ks_test'))

    def __eq__(self, other):
        return (isinstance(other, type(self))
                and self.config == other.config
                and self.comparators == other.comparators)

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash(json.dumps(self.config, sort_keys=True))
