#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call
from json import dumps
import os
import argparse
import shutil


def autodqm_offline(sample, data_run, ref_run):
    # Setup parameters
    params = {
        'sample': 'SingleMuon',
        'data_info': data_run,
        'ref_info': ref_run,
        'user_id': 'offline'
    }

    # Change to source directory
    os.chdir('src/scripts')
    do_cmd = './do.sh'

    # Run data retrieval and AutoDQM processing

    print("\nRetrieving data root files")
    params['type'] = 'retrieve_data'
    call([do_cmd, params['type'], params['user_id'], dumps(params)])

    print("\nRetrieving ref root files")
    params['type'] = 'retrieve_ref'
    call([do_cmd, params['type'], params['user_id'], dumps(params)])

    print("\nProcessing files")
    params['type'] = 'process'
    call([do_cmd, params['type'], params['user_id'], dumps(params)])

    os.chdir('../..')


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy_files(fromDir, toDir):
    for f in os.listdir(fromDir):
        shutil.copy(fromDir + f, toDir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run AutoDQM offline.')
    parser.add_argument('sample', type=str,
                        help="run sample, one of [Cosmics, SingleMuon]")
    parser.add_argument('data', type=str, help="data run number")
    parser.add_argument('ref', type=str, help="ref run number")
    parser.add_argument('-o', '--output', default='./offline/',
                        help="output directory")
    args = parser.parse_args()

    autodqm_offline(args.sample, args.data, args.ref)

    # Prepare and move files into output directory
    make_dir(args.output)
    make_dir(args.output + '/pdfs')
    make_dir(args.output + '/pngs')
    make_dir(args.output + '/txts')

    copy_files('./data/pdfs/offline/', args.output + '/pdfs')
    copy_files('./data/pngs/offline/', args.output + '/pngs')
    copy_files('./data/txts/offline/', args.output + '/txts')

    print("Results are available in the {0}".format(args.output))
