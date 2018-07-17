#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import json
from glob import glob
from tqdm import tqdm
from autodqm import dqm
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
    print('')
    print("Getting data root file...")
    data_path = get_run(data_series, data_sample, data_run, cert)

    print('')
    print("Getting reference root file...")
    ref_path = get_run(ref_series, ref_sample, ref_run, cert)

    print('')
    print("Loading configuration...")
    with open(config_path) as config_file:
        config = json.load(config_file)

    print('')
    print("Processing results...")
    results = process(config, subsystem,
                      data_series, data_sample, data_run, data_path,
                      ref_series, ref_sample, ref_run, ref_path,
                      output_dir=output_dir, plugin_dir=plugin_dir)

    print('')
    print("Results available in {}".format(output_dir))
    return results


def get_run(series, sample, run, cert):
    stream = dqm.stream_run(series, sample, run, cert)
    first = stream.next()
    path = first.path
    if first.cur == first.total:
        print("Run cached at {}".format(path))
    else:
        with tqdm(total=first.total,
                  unit='B', unit_scale=True, unit_divisor=1024) as t:
            prev = 0
            for p in stream:
                t.update(p.cur - prev)
                prev = p.cur
    return path


def make_cert(sslcert, sslkey, cainfo):
    return (sslcert, sslkey, cainfo)


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
    parser.add_argument('--cainfo', type=str, default='/etc/ssl/certs/ca-bundle.crt',
                        help="path to CERN CA files")
    args = parser.parse_args()

    sslcert = find_file(args.sslcert)
    sslkey = find_file(args.sslkey)
    os.environ['REQUESTS_CA_BUNDLE'] = args.cainfo
    autodqm_offline(args.subsystem,
                    args.data_run, args.data_sample, args.data_series,
                    args.ref_run, args.ref_sample, args.ref_series,
                    config_path=args.config,
                    output_dir=args.output,
                    plugin_dir=args.plugins,
                    sslcert=sslcert, sslkey=sslkey, cainfo=args.cainfo)
