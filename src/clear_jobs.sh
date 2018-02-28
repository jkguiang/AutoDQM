#!/bin/sh

cur_dir=/home/users/${USER}/public_html/AutoDQM/data

data=$cur_dir/data
ref=$cur_dir/ref
pngs=$cur_dir/pngs
pdfs=$cur_dir/pdfs
txts=$cur_dir/txts

to_clear=( ${data} ${ref} ${pngs} ${pdfs} ${txts} )

echo "Clearing jobs $date"

for parent in ${to_clear[@]} ; do

    for dir in $parent/* ; do

        cur_time=$(date +%s)
        mod_time=$(stat -c %Y "$dir")

        diff=$(( cur_time - mod_time ))
        day=$(( 24 * 60 * 60 ))

        if [[ "$diff" -ge "$day" ]] ; then
            echo "Deleted $dir"
            rm -r $dir
        fi

    done

done

echo "Done"
