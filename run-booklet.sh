#!/bin/bash
projetu-book --page-template=page.md --template=booklet.md --type tb --school-year 2021/2022
xelatex booklet_2020.tex
xelatex booklet_2020.tex
xelatex booklet_2020.tex
makeindex booklet_2020
texindy -L french -C utf8 booklet_2020.idx
xelatex booklet_2020.tex
xelatex booklet_2020.tex
xelatex booklet_2020.tex
#open booklet_2020.pdf