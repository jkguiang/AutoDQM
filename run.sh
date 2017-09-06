# $1={program select} $2={selected program options}
# $1=setup -> Check for required files, make directories, run {doAll, ooplt, mkjson}
# $1=plot -> run ooplt, check to see if any new pdf's made, if new pdfs => pdf_to_png()
# $1=scan -> run doAll

#Takes all .pdf's from pdf_dir and converts them to .png's at png_dir
pdf_to_png(){

    # $1=pdf_dir, $2=png_dir, $3=png_qual

    echo -n "Working: ["
    for file in ${1}/*.pdf ; do
        
        pdf_name=${file##*/}
        convert -density ${3} -trim -fuzz 1% $file ${2}/${pdf_name%.pdf}.png
        echo -n "#"

    done

    echo -n "]"
    echo " "

}

# Check for required files, make directories, run {doAll, ooplt, mkjson}
setup(){

    # Target Directories
    main_dir=$1
    pdf_dir=${main_dir}/pdfs
    png_dir=${main_dir}/pngs
    txt_dir=${main_dir}/txts
    png_qual=$2

    # Check if directories already exist
    if ! [[ -e ${pdf_dir} || -e ${png_dir} ]] ; then
        mkdir ${main_dir}
        mkdir ${pdf_dir} ${png_dir} ${txt_dir}

        # Copy files to proper directories and modify permissions
        cp index.php ${main_dir}
        chmod 755 ${main_dir}/index.php
        echo 'Finished.'
        exit 0
    
    else
        echo 'AutoDQM already installed.'
        exit 0

    fi

}


# Run AutoDQM
scan(){

    main_dir=$1
    pdf_dir=${main_dir}/pdfs
    png_dir=${main_dir}/pngs
    txt_dir=${main_dir}/txts
    png_qual=$2

    if [[ -e ${main_dir} ]] ; then
        rm -rf ${pdf_dir}/*
        rm -rf ${png_dir}/*
        rm -rf ${txt_dir}/*

        echo 'Scanning data...'
        python AutoDQM.py

        echo 'Updating web interface...'
        pdf_to_png ${pdf_dir} ${png_dir} ${png_qual} 
        chmod -R 755 ${pdf_dir}
        chmod -R 755 ${png_dir}
        chmod -R 755 ${txt_dir}
        chmod -R 755 ${main_dir}
        echo 'Finished.'
        exit 0

    else
        echo 'Please run setup command first.'
        exit 0
    fi
}

# Delete all relevant files
clean(){
    rm -r $1
}

# Default
main_dir=/home/users/${USER}/public_html/dqm_test
png_qual=50

if [ "$1" == "setup" ] ; then
    shift
    setup ${main_dir} ${png_qual}
    exit 0
elif [ "$1" == "scan" ] ; then
    shift
    scan ${main_dir} ${png_qual}
    exit 0
elif [ "$1" == "clean" ] ; then
    shift
    clean ${main_dir}
    exit 0
else
    echo 'Error: Invalid command'
    exit 1

fi
