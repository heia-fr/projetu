#!/bin/bash

projetu-book  --project-path=tb-2019-2020 --config=tb-2019-2020.yml --page-template=tb-page.md --template=booklet.md
xelatex booklet_2020.tex
makeindex booklet_2020
texindy -L french -C utf8 booklet_2020.idx
xelatex booklet_2020.tex
xelatex booklet_2020.tex
open booklet_2020.pdf