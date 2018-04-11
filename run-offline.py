#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call
from json import dumps
import os
import argparse
import shutil

# Retrieves data and reference root files, then runs AutoDQM on them


def autodqm_offline(series, sample, subsystem, data_run, ref_run):
    # Setup parameters
    params = {
        'series': series,
        'sample': sample,
        'subsystem': subsystem,
        'data_info': data_run,
        'ref_info': ref_run,
        'user_id': 'offline'
    }

    # Change to source directory
    os.chdir('src/')
    do_cmd = './do.sh'

    # Run data retrieval and AutoDQM processing

    print("\nRetrieving data root files")
    params['type'] = 'retrieve_data'
    call(['python', 'index.py', dumps(params)])

    print("\nRetrieving ref root files")
    params['type'] = 'retrieve_ref'
    call(['python', 'index.py', dumps(params)])

    print("\nProcessing files")
    params['type'] = 'process'
    call(['python', 'index.py', dumps(params)])

    os.chdir('../')


# Makes a directory iff it doesn't exist
def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Copies files from one directory to another


def copy_files(fromDir, toDir):
    for f in os.listdir(fromDir):
        shutil.copy(fromDir + f, toDir)


if __name__ == '__main__':

    # Collect command line arguments
    parser = argparse.ArgumentParser(description='Run AutoDQM offline.')
    parser.add_argument('series', type=str,
                        help="series to look for samples in. Examples: Run2017, Commissioning2018")
    parser.add_argument('sample', type=str,
                        help="sample to look for runs in. Examples: ZeroBias, SingleMuon, Cosmics")
    parser.add_argument('subsystem', type=str,
                        help="subsystem configuration to use. Examples: CSC, EMTF")
    parser.add_argument('data', type=str, help="data run number")
    parser.add_argument('ref', type=str, help="ref run number")
    parser.add_argument('-o', '--output', default='./offline/',
                        help="artifact (pdfs, pngs, txts) output directory")
    args = parser.parse_args()

    # Set environment variables to defaults if they're not already set
    if 'ADQM_CONFIG' not in os.environ:
        os.environ['ADQM_CONFIG'] = os.path.abspath('./configs.json')
    if 'ADQM_DB' not in os.environ:
        os.environ['ADQM_DB'] = os.path.abspath('./db/')
    if 'ADQM_TMP' not in os.environ:
        os.environ['ADQM_TMP'] = os.path.abspath('./tmp/')
    if 'ADQM_SSLCERT' not in os.environ:
        os.environ['ADQM_SSLCERT'] = '/tmp/x509up_u%s' % str(os.getuid())

    make_dir(os.environ['ADQM_DB'])
    make_dir(os.environ['ADQM_TMP'])

    autodqm_offline(args.series, args.sample, args.subsystem, args.data, args.ref)

    # Prepare and move files into output directory
    make_dir(args.output)
    make_dir(args.output + '/pdfs')
    make_dir(args.output + '/pngs')
    make_dir(args.output + '/txts')

    copy_files(os.environ['ADQM_TMP'] + 'offline/pdfs/', args.output + '/pdfs')
    copy_files(os.environ['ADQM_TMP'] + 'offline/pngs/', args.output + '/pngs')
    copy_files(os.environ['ADQM_TMP'] + 'offline/txts/', args.output + '/txts')

    print("Results are available in the {0}".format(args.output))
