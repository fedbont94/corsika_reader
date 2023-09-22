#!/bin/sh

PYTHON=/home/fbontempo/virtual_env/bin/python3
SCRIPT=/home/fbontempo/getMuonsFromCorsika/plot_muons.py

# Proton
$PYTHON $SCRIPT \
    --inputDir /data/user/fbontempo/corsikaMuons/proton/22335/ \
    --outputDir /home/fbontempo/getMuonsFromCorsika/plots/ \
    --year 2012 \
    --zenith_cut 38.0 
    