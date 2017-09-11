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

setup() {
    # Update html page
    pdf_dir=$PWD/pdfs
    png_dir=$PWD/pngs
    txt_dir=$PWD/txts
    png_qual=$2

    dir_array=( ${pdf_dir} ${png_dir} ${txt_dir} )

    for dir in ${dir_array[@]} ; do

        if ! [[ -e ${dir} ]] ; then
            mkdir ${dir} 
        fi

    done
    exit 0

}

updt() {
    rm -rf ${pdf_dir}/*
    rm -rf ${png_dir}/*
    rm -rf ${txt_dir}/*

    if ! [ "$(ls -A ${pdf_dir})" ] ; then
        exit 1
    fi

    pdf_to_png ${pdf_dir} ${png_dir} 30 
    chmod -R 755 ${pdf_dir}
    chmod -R 755 ${png_dir}
    chmod -R 755 ${txt_dir}
    chmod -R 755 $PWD
    exit 0
}

if [ $1 == "scan" ] ; then
    setup
fi
if [ $1 == "updt" ] ; then
    updt
fi
