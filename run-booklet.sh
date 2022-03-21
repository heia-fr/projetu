#!/bin/bash
projetu-book --page-template=tb-page.md --template=booklet.md --type ps6 --schoolyear 2021/2022
xelatex booklet_2020.tex
xelatex booklet_2020.tex
xelatex booklet_2020.tex
makeindex booklet_2020
texindy -L french -C utf8 booklet_2020.idx
xelatex booklet_2020.tex
xelatex booklet_2020.tex
xelatex booklet_2020.tex
#open booklet_2020.pdf