main_dir=${PWD}/data

# Build required directories
req_dirs=( ${main_dir}/pdfs ${main_dir}/pngs ${main_dir}/txts ${main_dir}/database )
for dir in "${req_dirs[@]}" ; do
    if ! [[ -e $dir ]] ; then
        mkdir $dir
        chmod -R 755 $dir
	echo "Created $dir"
    fi
done

cd ${PWD}/src/scripts

if [[ ${new_db} == $true ]] ; then
    python database.py build 
else
    python database.py map
fi
