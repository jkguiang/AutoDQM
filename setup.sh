main=${PWD}/src
req_dirs=( ${main}/data ${main}/ref ${main}/pdfs ${main}/pngs ${main}/txts ${main}/temp )

for dir in "${req_dirs[@]}" ; do
    if ! [[ -e $dir ]] ; then
        mkdir $dir
        chmod -R 755 $dir
    fi
done
