#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import ROOT
from autodqm import cfg
from autodqm.histpair import HistPair


def process(config_dir, subsystem,
            data_series, data_sample, data_run, data_path,
            ref_series, ref_sample, ref_run, ref_path,
            output_dir='./out/', plugin_dir='./plugins/'):

    # Ensure no graphs are drawn to screen and no root messages are sent to
    # terminal
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    # Report only errors to stderr
    ROOT.gErrorIgnoreLevel = ROOT.kWarning + 1

    histpairs = compile_histpairs(config_dir, subsystem,
                                  data_series, data_sample, data_run, data_path,
                                  ref_series, ref_sample, ref_run, ref_path)

    for d in [output_dir + s for s in ['/pdf', '/info', '/png', '/data_json', '/ref_json', '/plot_json']]:
        if not os.path.exists(d):
            os.makedirs(d)

    hist_outputs = []

    comparator_funcs = load_comparators(plugin_dir)
    for hp in histpairs:
        try:
            comparators = [(c, comparator_funcs[c]) for c in hp.comparators]
        except KeyError as e:
            raise error("Comparator {} was not found.".format(str(e)))

        for comp_name, comparator in comparators:
            result_id = identifier(hp, comp_name)
            info_path = '{}/info/{}.json'.format(output_dir, result_id)
            plot_json_path = '{}/plot_json/{}.json'.format(output_dir, result_id)
            data_json_path = '{}/data_json/{}.json'.format(output_dir, result_id)
            ref_json_path = '{}/ref_json/{}.json'.format(output_dir, result_id)
            pdf_path = '{}/pdf/{}.pdf'.format(output_dir, result_id)
            png_path = '{}/png/{}.png'.format(output_dir, result_id)

            if not os.path.isfile(info_path):
                results = comparator(hp, **hp.config)

                # Continue if no results
                if not results:
                    continue

                # Make plot json
                json_str = str(ROOT.TBufferJSON.ConvertToJSON(results.canvas))
                with open(plot_json_path, 'w') as jf:
                    json.dump(json_str, jf)

                # Make data json
                json_str = str(ROOT.TBufferJSON.ConvertToJSON(hp.data_hist))
                with open(data_json_path, 'w') as jf:
                    json.dump(json_str, jf)

                # Make data json
                json_str = str(ROOT.TBufferJSON.ConvertToJSON(hp.ref_hist))
                with open(ref_json_path, 'w') as jf:
                    json.dump(json_str, jf)

                # Make pdf
                results.canvas.Update()
                results.canvas.SaveAs(pdf_path)

                # Make png
                subprocess.Popen(
                    ['convert', '-density', '50', '-trim', '-fuzz', '1%', pdf_path, png_path])

                # Make info
                paths = {
                    'info': info_path,
                    'plot_json': plot_json_path,
                    'data_json': data_json_path,
                    'ref_json': ref_json_path,
                    'pdf': pdf_path,
                    'png': png_path,
                }
                info = {
                    'id': result_id,
                    'name': hp.data_name,
                    'comparator': comp_name,
                    'always_show': hp.config.get('always_show', False),
                    'anomalous': results.show,
                    'config': hp.config,
                    'results': results.info,
                    'paths': paths
                }
                with open(info_path, 'w') as jf:
                    json.dump(info, jf)
            else:
                with open(info_path) as jf:
                    info = json.load(jf)

            hist_outputs.append(info)

    return hist_outputs


def compile_histpairs(config_dir, subsystem,
                      data_series, data_sample, data_run, data_path,
                      ref_series, ref_sample, ref_run, ref_path):

    config = cfg.get_subsystem(config_dir, subsystem)
    # Histogram details
    conf_list = config["hists"]
    main_gdir = config["main_gdir"]

    # ROOT files
    data_file = ROOT.TFile.Open(data_path)
    ref_file = ROOT.TFile.Open(ref_path)

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

            # This try/catch is a dirty way of checking that this objects are something plottable
            try:
                data_hist.SetDirectory(0)
                ref_hist.SetDirectory(0)
            except:
                continue

            hPair = HistPair(hconf,
                             data_series, data_sample, data_run, name, data_hist,
                             ref_series, ref_sample, ref_run, name, ref_hist)
            histPairs.append(hPair)

    data_file.Close()
    ref_file.Close()
    return histPairs


def load_comparators(plugin_dir):
    """Load comparators from each python module in ADQM_PLUGINS."""

    sys.path.insert(0, plugin_dir)

    comparators = dict()

    for modname in os.listdir(plugin_dir):
        if modname[0] == '_' or modname[-4:] == '.pyc':
            continue
        if modname[-3:] == '.py':
            modname = modname[:-3]
        try:
            mod = __import__("{}".format(modname))
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
