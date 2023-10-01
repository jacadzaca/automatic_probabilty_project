#!/usr/bin/env sh

# [First Name] [Last Name] s[student index].[student index]

stat pdfs &> /dev/null || mkdir pdfs
stat tex_files &> /dev/null || mkdir tex_files
while read -r line; do
    name=$(echo "$line" | cut -d '.' -f1)
    index=$(echo "$line" | cut -d '.' -f2)
    output=$(echo "$name" | cut -d ',' -f1 | tr ' ' '_')
    echo "$name" "$index"
    ./generate_homework.py "$name" "$index" > "tex_files/$output.tex"
    pdflatex --output-dir "pdfs" "tex_files/$output.tex" &&
        ps2pdf "pdfs/$output.pdf" "pdfs/tmp.pdf" &&
        mv "pdfs/tmp.pdf" "pdfs/$output.pdf"
    rm -f pdfs/*aux pdfs/*log pdfs/*out
done < input.txt
rm -f pdfs/temp.pdf

