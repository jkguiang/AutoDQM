main=${PWD}/src

# Build required directories
req_dirs=( ${main}/data ${main}/ref ${main}/pdfs ${main}/pngs ${main}/txts ${main}/temp ${main}/CGI/database )
for dir in "${req_dirs[@]}" ; do
    if ! [[ -e $dir ]] ; then
        mkdir $dir
        chmod -R 755 $dir
	echo "Created $dir"
    fi
done

# Build database
db=${main}/CGI/database
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

cd ${PWD}/src/CGI

if [[ ${new_db} == $true ]] ; then
    python database.py build 
else
    python database.py map
fi
