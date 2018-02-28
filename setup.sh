main_dir=${PWD}/data

# Build required directories
req_dirs=( ${main_dir}/data ${main_dir}/ref ${main_dir}/pdfs ${main_dir}/pngs ${main_dir}/txts ${main_dir}/temp ${main_dir}/database )
for dir in "${req_dirs[@]}" ; do
    if ! [[ -e $dir ]] ; then
        mkdir $dir
        chmod -R 755 $dir
	echo "Created $dir"
    fi
done

# Build database
db=${main_dir}/database
new_db=$false
db_dirs=( ${db}/Run2017 ${db}/Run2017/SingleMuon ${db}/Run2017/Cosmics )
for dir in "${db_dirs[@]}" ; do
    if ! [[ -e $dir ]] ; then
        new_db=$true
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
