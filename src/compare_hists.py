#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import subprocess
import ROOT
import AutoDQM
from yapsy.PluginManager import PluginManager
from histpair import HistPair


def process(user_id, subsystem, query_info):
    data_fname = "{0}/{1}/{2}/{3}.root".format(
        os.environ["ADQM_DB"], query_info["data_series"], query_info["data_sample"], query_info["data_run"])
    ref_fname = "{0}/{1}/{2}/{3}.root".format(
        os.environ["ADQM_DB"], query_info["ref_series"], query_info["ref_sample"], query_info["ref_run"])

    # Ensure no graphs are drawn to screen and no root messages are sent to terminal
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    histpairs = compile_histpairs(subsystem, data_fname,
                                  ref_fname, query_info["data_run"], query_info["ref_run"])

    tmp_dir = os.getenv('ADQM_TMP') + user_id + '/'
    hist_outputs = []

    comparator_funcs = load_comparators()
    for hp in histpairs:
        for comparator in (comparator_funcs[c] for c in hp.comparators):
            pdf_path = '{}/pdfs/{}.pdf'.format(tmp_dir, hash(hp))
            json_path = '{}/jsons/{}.json'.format(tmp_dir, hash(hp))
            png_path = '{}/pngs/{}.png'.format(tmp_dir, hash(hp))

            if not os.path.isfile(json_path):
                canvas, show, results_info = comparator(
                    hp, outfile, **query_info)

                # Make pdf
                canvas.SaveAs(pdf_path)

                # Make png
                subprocess.Popen(
                    ['convert', '-density', '50', '-trim', '-fuzz', '1%', pdf_path, png_path])

                # Make json
                info = {
                    'pdf_path': pdf_path,
                    'json_path': json_path,
                    'png_path': png_path,
                    'display': show or hp.config['always_show'],
                    'config': hp.config,
                    'results': results_info,
                }
                with open(json_path) as jf:
                    json.dump(info, jf)
            else:
                with open(json_path) as jf:
                    info = json.load(jf)

            hist_outputs.append(info)

    return hist_outputs


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
            raise error(
                "Subsystem dir {0} not found in data root file".format(data_dirname))
        if not ref_dir:
            raise error(
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


def load_comparators():
    """Load comparators from each python module in ADQM_PLUGINS."""

    plugin_dir = os.getenv('ADQM_PLUGINS')

    comparators = dict()

    # Load all plugins in the plugin dir
    pm = PluginManager()
    pm.setPluginPlaces([plugin_dir])
    pm.collectPlugins()

    # Collect new comparators from each loaded plugin
    for pluginInfo in pm.getAllPlugins():
        pm.activatePluginByName(pluginInfo.name)
        try:
            new_comps = pluginInfo.plugin_object.comparators()
            comparators.update(new_comps)
        except AttributeError:
            raise error(
                "Plugin {} does not have a comparators() function.".format(pluginInfo.name))


class error(Exception):
    pass
