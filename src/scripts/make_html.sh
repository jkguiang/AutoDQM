#!/bin/sh
pardir="$(dirname "$PWD")"
parpardir="$(dirname "$pardir")"
main_dir=$parpardir/data

#Takes all .pdf's from pdf_dir and converts them to .png's at png_dir
pdf_to_png(){

    # $1=pdf_dir, $2=png_dir, $3=png_qual

    for file in ${1}/*.pdf ; do
        
        pdf_name=${file##*/}
        convert -density ${3} -trim -fuzz 1% $file ${2}/${pdf_name%.pdf}.png

    done

}

setup() {
    # Update html page
    user_id=$1
    pdf_dir=$main_dir/pdfs/${user_id}
    png_dir=$main_dir/pngs/${user_id}
    txt_dir=$main_dir/txts/${user_id}

    dir_array=( ${pdf_dir} ${png_dir} ${txt_dir} )

    for dir in ${dir_array[@]} ; do

        if ! [[ -e ${dir} ]] ; then
            mkdir ${dir} 
        fi

    rm -rf ${pdf_dir}/*
    rm -rf ${txt_dir}/*

    done
    exit 0

}

updt() {
    # Update html page
    user_id=$1
    pdf_dir=$main_dir/pdfs/${user_id}
    png_dir=$main_dir/pngs/${user_id}
    txt_dir=$main_dir/txts/${user_id}

    rm -rf ${png_dir}/*

    pdf_to_png ${pdf_dir} ${png_dir} 50 
    chmod -R 755 ${pdf_dir}
    chmod -R 755 ${png_dir}
    chmod -R 755 ${txt_dir}
    chmod -R 755 $main_dir
    exit 0
}

if [ $1 == "setup" ] ; then
    shift
    setup $1
fi
if [ $1 == "updt" ] ; then
    shift
    updt $1
fi
