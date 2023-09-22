#!/bin/sh

ENV=/data/user/fbontempo/icetray/build/env-shell.sh
PYTHON=/home/fbontempo/virtual_env/bin/python3 
SCRIPT=/home/fbontempo/getMuonsFromCorsika/submit_multiple_readCorsika.py

# Gammas 2012
$PYTHON $SCRIPT \
    --input_directory /data/sim/IceTop/2023/generated/CORSIKA_SIBYLL2.3d/gamma/22334/ \
    --output_directory /data/user/fbontempo/corsikaMuons/gamma/22334/ \
    --year 2012 \
    --primary "gamma" \
    --energyStart 4.0 \
    --energyEnd 7.0 \
    --energyCut 273.0


# Protons 2012
$PYTHON $SCRIPT \
    --input_directory /data/sim/IceTop/2023/generated/CORSIKA_SIBYLL2.3d/proton/22335/ \
    --output_directory /data/user/fbontempo/corsikaMuons/proton/22335/ \
    --year 2012 \
    --primary "proton" \
    --energyStart 4.0 \
    --energyEnd 7.0 \
    --energyCut 273.0

#######################################################################


