#!/bin/bash

# CMSSW_VER=CMSSW_7_4_4

# export PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/bin:$PATH
# export PYTHONPATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/py2-pycurl/7.19.0-cms/lib/python2.7/site-packages:$PYTHONPATH
# export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/lib:$LD_LIBRARY_PATH

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw/CMSSW_9_2_8; eval `/cvmfs/cms.cern.ch/common/scramv1 runtime -sh`; cd ~-

if [[ "$1" == "retrieve" ]] ; then
    shift
    python index.py "$*"

elif [[ "$1" == "search" ]] ; then
    shift
    python search.py "$*"
elif [[ "$1" == "refresh" ]] ; then
    if ! [[ -e new_files.json ]] ; then
        touch new_files.json
    fi
    shift
    python cron_dqm.py "$*"
    chmod 755 new_files.json
else
    echo 'Invalid command.'
    exit 1
fi
# python test.py $*
