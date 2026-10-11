#!/bin/sh
# Build main.pdf with pdflatex + bibtex, as the CVPR kit expects.
pdflatex -interaction=nonstopmode main >/dev/null
bibtex main >/dev/null
pdflatex -interaction=nonstopmode main >/dev/null
pdflatex -interaction=nonstopmode main | grep -E '^!|Output written|Warning|Overfull' | grep -v "Font" | head -20
