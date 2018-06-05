#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import tempfile
import ROOT
import AutoDQM
from histpair import HistPair


def process(subsystem,
            data_series, data_sample, data_run,
            ref_series, ref_sample, ref_run):

    # Ensure no graphs are drawn to screen and no root messages are sent to terminal
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    histpairs = compile_histpairs(subsystem,
                                  data_series, data_sample, data_run,
                                  ref_series, ref_sample, ref_run)

    out_dir = os.getenv('ADQM_TMP') + 'out'
    for d in [out_dir + s for s in ['/pdfs', '/jsons', '/pngs']]:
        if not os.path.exists(d):
            os.makedirs(d)

    hist_outputs = []
    tmp_dir = tempfile.mkdtemp()
    tmp_file = ROOT.TFile('{}/temp.root', 'RECREATE')

    comparator_funcs = load_comparators()
    for hp in histpairs:
        try:
            comparators = [(c, comparator_funcs[c]) for c in hp.comparators]
        except KeyError as e:
            raise error("Comparator {} was not found.".format(str(e)))

        for comp_name, comparator in comparators:
            filename = identifier(hp, comp_name)
            pdf_path = '{}/pdfs/{}.pdf'.format(out_dir, filename)
            json_path = '{}/jsons/{}.json'.format(out_dir, filename)
            png_path = '{}/pngs/{}.png'.format(out_dir, filename)

            if not os.path.isfile(json_path):
                results = comparator(hp, **hp.config)

                # Continue if no results
                if not results:
                    continue
                
                # Make pdf
                results.canvas.Update()
                results.canvas.SaveAs(pdf_path)

                # Make png
                subprocess.Popen(
                    ['convert', '-density', '50', '-trim', '-fuzz', '1%', pdf_path, png_path])

                # Make json
                info = {
                    'pdf_path': pdf_path,
                    'json_path': json_path,
                    'png_path': png_path,
                    'display': results.show or hp.config.get('always_show', False),
                    'config': hp.config,
                    'results': results.info,
                }
                with open(json_path, 'w') as jf:
                    json.dump(info, jf)
            else:
                with open(json_path) as jf:
                    info = json.load(jf)

            hist_outputs.append(info)

    tmp_file.Close()

    return hist_outputs


def compile_histpairs(subsystem,
                      data_series, data_sample, data_run,
                      ref_series, ref_sample, ref_run):

    # Root files
    data_fname = "{0}/{1}/{2}/{3}.root".format(
        os.environ["ADQM_DB"], data_series, data_sample, data_run)
    ref_fname = "{0}/{1}/{2}/{3}.root".format(
        os.environ["ADQM_DB"], ref_series, ref_sample, ref_run)

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

            hPair = HistPair(hconf,
                             data_series, data_sample, data_run, name, data_hist,
                             ref_series, ref_sample, ref_run, name, ref_hist)
            histPairs.append(hPair)

    data_file.Close()
    ref_file.Close()
    return histPairs


def load_comparators():
    """Load comparators from each python module in ADQM_PLUGINS."""

    plugin_dir = os.getenv('ADQM_PLUGINS')
    sys.path.insert(0, plugin_dir)

    comparators = dict()

    for modname in os.listdir(plugin_dir):
        if modname[-3:] == '.py':
            modname = modname[:-3]
        mod = __import__("{}".format(modname))
        try:
            new_comps = mod.comparators()
        except AttributeError:
            raise error(
                "Plugin {} does not have a comparators() function.".format(mod))
        comparators.update(new_comps)

    return comparators


def identifier(hp, comparator_name):
    """Return a `hashed` identifier for the histpair"""
    data_id = "DATA-{}-{}-{}".format(hp.data_series,
                                     hp.data_sample, hp.data_run)
    ref_id = "REF-{}-{}-{}".format(hp.ref_series, hp.ref_sample, hp.ref_run)
    if hp.data_name == hp.ref_name:
        name_id = hp.data_name
    else:
        name_id = "DATANAME-{}_REFNAME-{}".format(hp.data_name, hp.ref_name)
    comp_id = "COMP-{}".format(comparator_name)

    hash_snippet = str(hash(hp))[-5:]

    idname = "{}_{}_{}_{}_{}".format(
        data_id, ref_id, name_id, comp_id, hash_snippet)
    return idname


class error(Exception):
    pass
