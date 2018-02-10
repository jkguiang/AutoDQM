#!/bin/bash

# CMSSW_VER=CMSSW_7_4_4

# export PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/bin:$PATH
# export PYTHONPATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/py2-pycurl/7.19.0-cms/lib/python2.7/site-packages:$PYTHONPATH
# export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/lib:$LD_LIBRARY_PATH

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw/CMSSW_9_2_8; eval `/cvmfs/cms.cern.ch/common/scramv1 runtime -sh`; cd ~-

if [[ "$1" == "retrieve_data" || "$1" == "retrieve_ref" || "$1" == "process" ]] ; then
    if [[ "$1" == "retrieve_data" ]] ; then
        shift
        if [[ -e $PWD/data/$1 ]] ; then
            rm $PWD/data/$1/*
        else
            mkdir $PWD/data/$1
            chmod 755 -R $PWD/data/$1
        fi
    fi
    if [[ "$1" == "retrieve_ref" ]] ; then
        shift
        if [[ -e $PWD/ref/$1 ]] ; then
            rm $PWD/ref/$1/*
        else
            mkdir $PWD/ref/$1
            chmod 755 -R $PWD/ref/$1
        fi
    fi
    if [[ "$1" == "process" ]] ; then
        shift
    fi
    shift
    python index.py "$*"

elif [[ "$1" == "search" ]] ; then
    shift
    shift
    python search.py "$*"
elif [[ "$1" == "refresh" ]] ; then
    if ! [[ -e db_map.json ]] ; then
        touch db_map.json
    fi
    shift
    shift
    python database.py map
    chmod 755 db_map.json
else
    echo 'Invalid command.'
    exit 1
fi
