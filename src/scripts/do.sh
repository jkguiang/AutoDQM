#!/bin/bash

# CMSSW_VER=CMSSW_7_4_4

# export PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/bin:$PATH
# export PYTHONPATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/py2-pycurl/7.19.0-cms/lib/python2.7/site-packages:$PYTHONPATH
# export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/lib:$LD_LIBRARY_PATH

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw/CMSSW_9_2_8; eval `/cvmfs/cms.cern.ch/common/scramv1 runtime -sh`; cd ~-

pardir="$(dirname "$PWD")"
parpardir="$(dirname "$pardir")"
main_dir=$parpardir/data
if [[ "$1" == "retrieve_data" || "$1" == "retrieve_ref" || "$1" == "process" ]] ; then
    shift
    python index.py "$*"

elif [[ "$1" == "search" ]] ; then
    shift
    shift
    python search.py "$*"
elif [[ "$1" == "refresh" ]] ; then
    if ! [[ -e $main_dir/db_map.json ]] ; then
        touch $main_dir/db_map.json
    fi
    shift
    shift
    python database.py map
    chmod 755 $main_dir/db_map.json
else
    echo 'Invalid command.'
    exit 1
fi
