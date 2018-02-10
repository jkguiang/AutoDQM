main=${PWD}/src

if [[ ${1} == "" ]] ; then
    echo "Please pass in subsystem acronym (i.e. CSC, DT, etc.)"
    exit 0
fi

req_dirs=( ${main}/data ${main}/ref ${main}/pdfs ${main}/pngs ${main}/txts ${main}/temp ${main}/CGI/${1}_db )

for dir in "${req_dirs[@]}" ; do
    if ! [[ -e $dir ]] ; then
        mkdir $dir
        chmod -R 755 $dir
	echo "Created $dir"
    fi
done

if [[ -e ${main}/CGI/${1}_db ]] ; then
    python ${PWD}/src/CGI/database.py map ${1}
else
    python ${PWD}/src/CGI/database.py build ${1}
fi
