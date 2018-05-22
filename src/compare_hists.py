#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import subprocess
import ROOT
import AutoDQM
from HistPair import HistPair


def process(user_id, subsystem, data_info, ref_info):
    data_fname = "{0}/{1}/{2}/{3}.root".format(
        os.environ["ADQM_DB"], data_info["series"], data_info["sample"], data_info["run"])
    ref_fname = "{0}/{1}/{2}/{3}.root".format(
        os.environ["ADQM_DB"], ref_info["series"], ref_info["sample"], ref_info["run"])

    histPairs = compile_histpairs(subsystem, data_fname,
                                  ref_fname, data_info["run"], ref_info["run"])

    tmp_dir = os.getenv('ADQM_TMP') + user_id + '/'
    AutoDQM.autodqm(histPairs, data_info["run"], ref_info["run"], tmp_dir)

    # Convert pdfs produced by AutoDQM to small pngs
    if not os.path.exists(tmp_dir + 'pngs'):
        os.makedirs(tmp_dir + 'pngs')
    for pdf in os.listdir(tmp_dir + 'pdfs'):
        subprocess.check_output(['convert', '-density', '50', '-trim', '-fuzz', '1%', str(
            tmp_dir + 'pdfs/' + pdf), str(tmp_dir + 'pngs/' + pdf.split('.')[0] + '.png')])

    return True, None


def compile_histpairs(subsystem, data_fname, ref_fname, data_run, ref_run):
    # Load config
    with open(os.getenv('ADQM_CONFIG')) as config_file:
        config = json.load(config_file)
    conf_list = config[subsystem]["hists"]
    main_gdir = config[subsystem]["main_gdir"]

    data_file = ROOT.TFile.Open(data_fname)
    ref_file = ROOT.TFile.Open(ref_fname)
    histPairs = []

    for hconf in conf_list:
        # Get name of hist in root file
        h = str(hconf["path"].split("/")[-1])
        # Get parent directory of hist
        gdir = str(hconf["path"].split(h)[0])

        data_dirname = "{0}{1}".format(main_gdir.format(data_run), gdir)
        ref_dirname = "{0}{1}".format(main_gdir.format(ref_run), gdir)

        data_dir = data_file.GetDirectory(data_dirname)
        ref_dir = ref_file.GetDirectory(ref_dirname)

        if not data_dir:
            raise Exception(
                "Subsystem dir {0} not found in data root file".format(data_dirname))
        if not ref_dir:
            raise Exception(
                "Subsystem dir {0} not found in ref root file".format(ref_dirname))

        data_keys = data_dir.GetListOfKeys()
        ref_keys = ref_dir.GetListOfKeys()

        valid_names = []

        # Add existing histograms that match h to valid_names
        if "*" not in h:
            if data_keys.Contains(h) and ref_keys.Contains(h):
                valid_names.append(h)
        else:
            # Check entire directory for files matching wildcard
            for name in [key.GetName() for key in data_keys]:
                if h.split("*")[0] in name and ref_keys.Contains(name):
                    valid_names.append(name)

        # Load the histograms and create HistPairs
        for name in valid_names:
            data_hist = data_dir.Get(name)
            ref_hist = ref_dir.Get(name)

            # TODO Check for THn, not THnF
            if not ((type(data_hist) == ROOT.TH1F or type(data_hist) == ROOT.TH2F)
                    and (type(ref_hist) == ROOT.TH1F or type(ref_hist) == ROOT.TH2F)):
                continue

            data_hist.SetDirectory(0)
            ref_hist.SetDirectory(0)

            hPair = HistPair(data_hist, ref_hist, hconf)
            histPairs.append(hPair)

    data_file.Close()
    ref_file.Close()
    return histPairs
