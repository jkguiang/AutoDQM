#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import argparse
import json
from glob import glob
from autodqm.cerncert import CernCert
from autodqm.fetch import fetch
from autodqm.compare_hists import process


def autodqm_offline(subsystem,
                    data_run, data_sample, data_series,
                    ref_run, ref_sample, ref_series,
                    config_path, output_dir, plugin_dir,
                    sslcert, sslkey, cainfo):

    if not ref_sample:
        ref_sample = data_sample
    if not ref_series:
        ref_series = data_series

    print("Using cert/key pair:")
    print("\tCertificate: {}".format(sslcert))
    print("\tKey: {}".format(sslkey))
    cert = make_cert(sslcert, sslkey, cainfo)

    # Get root files
    print("Getting data root file...")
    data_path = fetch(cert, data_series, data_sample, data_run)
    print("Getting reference root file...")
    ref_path = fetch(cert, ref_series, ref_sample, ref_run)

    print("Loading configuration...")
    with open(config_path) as config_file:
        config = json.load(config_file)

    print("Processing results...")
    results = process(config, subsystem,
                      data_series, data_sample, data_run, data_path,
                      ref_series, ref_sample, ref_run, ref_path,
                      output_dir=output_dir, plugin_dir=plugin_dir)

    print("Results available in {}".format(output_dir))
    return results


def make_cert(sslcert, sslkey, cainfo):
    return CernCert(sslcert, sslkey, cainfo)


def find_file(pattern):
    '''Find the first file that matches the given pattern.'''
    pattern = os.path.expandvars(pattern)
    pattern = os.path.expanduser(pattern)
    return next((f for f in glob(pattern)), None)


if __name__ == '__main__':

    # Collect command line arguments
    parser = argparse.ArgumentParser(description='Run AutoDQM offline.')
    parser.add_argument('subsystem', type=str,
                        help="subsystem configuration to use. Examples: CSC, EMTF")

    parser.add_argument('data_series', type=str,
                        help="data series to look for samples in. Examples: Run2017, Commissioning2018")
    parser.add_argument('data_sample', type=str,
                        help="data sample to look for runs in. Examples: ZeroBias, SingleMuon, Cosmics")
    parser.add_argument('data_run', type=str, help="data run number")
    parser.add_argument('ref_run', type=str, help="data run number")

    parser.add_argument('--ref_series', type=str, default=None,
                        help="ref series to look for samples in. Defaults to data_series")
    parser.add_argument('--ref_sample', type=str, default=None,
                        help="ref sample to look for runs in. Defaults to data_ref")

    parser.add_argument('-c', '--config', default='./configs.json',
                        help="config file to use")
    parser.add_argument('-o', '--output', default='./out/',
                        help="artifact (pdfs, pngs, txts) output directory")
    parser.add_argument('-p', '--plugins', default='./plugins/',
                        help="comparison plugins directory")

    parser.add_argument('--sslcert', type=str, default='~/.globus/usercert.*',
                        help="path to a CMS VO public certificate")
    parser.add_argument('--sslkey', type=str, default='~/.globus/userkey.*',
                        help="path to a CMS VO private key")
    parser.add_argument('--cainfo', type=str, default=None,
                        help="path to CERN CA files")
    args = parser.parse_args()

    sslcert = find_file(args.sslcert)
    sslkey = find_file(args.sslkey)
    autodqm_offline(args.subsystem,
                    args.data_run, args.data_sample, args.data_series,
                    args.ref_run, args.ref_sample, args.ref_series,
                    config_path=args.config,
                    output_dir=args.output,
                    plugin_dir=args.plugins,
                    sslcert=sslcert, sslkey=sslkey, cainfo=args.cainfo)
