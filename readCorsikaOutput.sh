#! /bin/sh

# ENV=/data/user/fbontempo/icetray/build/env-shell.sh
ENV=/data/user/mweyrauch/PhD/software/surface-array/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/getMuonsFromCorsika/readCorsikaMuons.py


eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

# Gamma 
echo "Gamma"
$ENV python $SCRIPT \
    --inputDir /data/sim/IceTop/2023/generated/CORSIKA_SIBYLL2.3d/gamma/22334/ \
    --outputDir /data/user/fbontempo/corsikaMuons/gamma/22334/ \
    --energy 6.0 \
    --energyCut 273.0

# Proton 
echo "Proton"
$ENV python $SCRIPT \
    --inputDir /data/sim/IceTop/2023/generated/CORSIKA_SIBYLL2.3d/proton/22335/ \
    --outputDir /data/user/fbontempo/corsikaMuons/proton/22335/ \
    --energy 6.0 \
    --energyCut 273.0
