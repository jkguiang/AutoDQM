from subprocess import call
from json import dumps
from os import chdir

def autodqm_offline(sample, data_run, ref_run):
    # Setup parameters
    params = {
            'sample': 'SingleMuon',
            'data_info': data_run,
            'ref_info': ref_run,
            'user_id': 'offline',
            }

    # Change to source directory
    chdir('src')
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

    print("Results are available in the src directory")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run AutoDQM offline.')
    parser.add_argument('sample', type=str, help="run sample, one of [Cosmics, SingleMuon]")
    parser.add_argument('data', type=int, help="data run number")
    parser.add_argument('ref', type=int, help="ref run number")
    args = parser.parse_args()

    autodqm_offline(args.sample, args.data, args.ref)

