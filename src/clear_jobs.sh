
data=$PWD/data
ref=$PWD/ref
pngs=$PWD/pngs
pdfs=$PWD/pdfs
txts=$PWD/txts

to_clear=( ${data} ${ref} ${pngs} ${pdfs} ${txts} )

for parent in ${to_clear[@]} ; do

    for dir in $parent/* ; do

        cur_time=$(date +%s)
        mod_time=$(stat -c %Y "$dir")

        diff=$(( cur_time - mod_time ))
        day=$(( 24 * 60 * 60 ))

        if [[ "$diff" -ge "$day" ]] ; then

            rm -r $dir

        else
            echo "NEW"
        fi

        echo $cur_time
        echo $mod_time
        echo $dir

    done

done
