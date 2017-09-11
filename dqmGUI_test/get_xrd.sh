#!/bin/bash

# Store target directory
targ_dir=$PWD/$1
shift

if ! [[ -e ${targ_dir} ]] ; then
    mkdir ${targ_dir}
fi

# Parse over input files
for var in "$@" ; do

    xrdcp root://xrootd.unl.edu//$var ${targ_dir}

done
