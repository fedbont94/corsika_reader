#!/usr/bin/env python3

"""
Reads the muons from the corsika MCTree and the relevant information from the I3MCTree
How to run:
environment: icetray surfacearray branch. Tested
python used: /cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`
env python3 readCorsikaMuons.py -i /path/to/corsika/energy/folders -o /path/to/output/dir --energyStart 4.0 --energyEnd 5.0 --energyCut 273.0
"""

import argparse
import glob
import os
import sys

import numpy as np
import pandas as pd

from icecube import (
    icetray,
    corsika_reader,
    phys_services,
    dataio,
    dataclasses,
)
from I3Tray import I3Tray

# Set worning to error to avoid warnings
icetray.logging.set_level("ERROR")


def parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--inputDir",
        help="where to read energy directories with the corsika files",
        default="",
    )
    parser.add_argument(
        "-o",
        "--outputDir",
        help="where to write the output file",
        default="",
    )
    parser.add_argument(
        "--energy",
        help="energy of the folder",
        default="",
        type=str,
    )

    parser.add_argument(
        "--energyCut",
        help="energy cut for the muon cut energy in GeV",
        default=0.0,
        type=float,
    )

    return parser


def __check_parser(
    args,
):
    """
    Checks all the arguments passed to the parser
    """

    if args.inputDir == "" or not os.path.isdir(args.inputDir):
        sys.exit("No input directory specified or directory does not exist")
    if args.outputDir == "" or not os.path.isdir(args.outputDir):
        sys.exit("No output directory specified or directory does not exist")
    if args.energy == "":
        sys.exit("No energy specified")
    if args.energyCut == 0.0:
        import warnings

        warnings.warn(
            "No energy cut specified, maybe is not what you want",
            stacklevel=2,
        )
    return


def get_NumbOfMuons(
    frame,
    data,
    idx,
    energy_cut,
):
    """
    Stores the information about the primary particle
    read the muons from the corsika MCTree
    count and store the number of muons above certain thresholds

    Note: primary particle is the first particle in the MCTree
    the type of the primary particle is consistent with the corsika manual
    as shown in the column "PYTHIA HERWIG (PDG)"
    eg.
    22: gamma
    +-11: e+-
    +-13: mu+-
    """

    tree = frame["I3MCTree"]
    primary = frame["I3MCTree"].get_primary(tree.get_primaries()[0])

    daughters = tree.get_daughters(tree.get_primaries()[0])
    muons = [
        d for d in daughters if np.abs(d.type) in [13]
    ]  # 13 si the key for muons in Pythia

    muon_energies = np.array(list(map(lambda p: p.energy, muons)))
    muons_above_Ecut = muon_energies >= energy_cut

    # Write the information in the data dict
    data["primary"][idx] = primary.type
    data["energy"][idx] = primary.energy
    data["x"][idx] = primary.pos.x
    data["y"][idx] = primary.pos.y
    data["zenith"][idx] = primary.dir.zenith
    data["azimuth"][idx] = primary.dir.azimuth
    data["total_muons"][idx] = len(muons)
    data["muons_above_Ecut"][idx] = np.sum(muons_above_Ecut)

    data["MCPrimary_FractionContainment"][idx] = frame[
        "MCPrimary_FractionContainment"
    ].value
    data["MCPrimary_inice_FractionContainment"][idx] = frame[
        "MCPrimary_inice_FractionContainment"
    ].value

    return


def calculate_containment(
    frame,
    scaling,
    particle="MCPrimary",
):
    """Calculate geometry containment values using Kath's method."""

    tree = frame["I3MCTree"]
    primary = frame["I3MCTree"].get_primary(tree.get_primaries()[0])

    frame.Put(
        particle + "_FractionContainment",
        dataclasses.I3Double(scaling.scale_icetop(primary)),
    )
    frame.Put(
        particle + "_inice_FractionContainment",
        dataclasses.I3Double(scaling.scale_inice(primary)),
    )


def tray_readCorsikaFile(
    corsika_file,
    data_dict,
    idx,
    energy_cut,
    scaling,
):
    """
    Creates a tray to read the corsika file
    and store the information in data_dict
    """

    tray = I3Tray()
    tray.context["I3RandomService"] = phys_services.I3GSLRandomService(42)
    tray.AddModule(
        "I3CORSIKAReader",
        FilenameList=[corsika_file],
        NEvents=1,
    )

    tray.Add(
        calculate_containment,
        scaling=scaling,
        particle="MCPrimary",
        streams=[icetray.I3Frame.DAQ],
    )

    tray.Add(
        get_NumbOfMuons,
        data=data_dict,
        energy_cut=energy_cut,
        idx=idx,
        streams=[icetray.I3Frame.DAQ],
    )

    tray.Execute()

    return


def main():
    args = parser().parse_args()
    __check_parser(args)

    # Define the output file name
    output_file = f"{args.outputDir}/{args.energy}_DataFrame.hdf5"

    # Check if the file already exists
    if os.path.isfile(output_file):
        sys.exit(f"File {output_file} already exists, skipping...")

    print("Energy:", args.energy)

    # Get all the files to be read
    files = sorted(glob.glob(f"{args.inputDir}/{args.energy}/*.bz2"))

    # Create the data dict to store the information depending on the number of files
    data_dict = {
        "primary": np.empty(len(files), dtype=None),
        "energy": np.empty(len(files), dtype=np.float64),
        "x": np.empty(len(files), dtype=np.float64),
        "y": np.empty(len(files), dtype=np.float64),
        "zenith": np.empty(len(files), dtype=np.float64),
        "azimuth": np.empty(len(files), dtype=np.float64),
        "total_muons": np.empty(len(files), dtype=np.int32),
        "muons_above_Ecut": np.empty(len(files), dtype=np.int32),
        "MCPrimary_FractionContainment": np.empty(len(files), dtype=np.float64),
        "MCPrimary_inice_FractionContainment": np.empty(len(files), dtype=np.float64),
    }
    gcd_file = "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2012.Run120844.T00S1.Pass2_V1b_Snow121021.i3.gz"

    scaling = None
    for frame in dataio.I3File(gcd_file):
        if frame.Stop == icetray.I3Frame.Geometry:
            scaling = phys_services.I3ScaleCalculator(frame["I3Geometry"])

    if scaling is None:
        sys.exit("Geometry not found")

    # Read all the files
    for idx, corsika_file in enumerate(files):
        # Skip non bz2 files
        if not corsika_file.endswith(".bz2"):
            continue
        # Print the progress
        if (idx + 1) % 100 == 0:
            print("Files read:", idx + 1)

        tray_readCorsikaFile(
            corsika_file=corsika_file,
            data_dict=data_dict,
            idx=idx,
            energy_cut=args.energyCut,
            scaling=scaling,
        )

    print("Writing file:", output_file)

    df = pd.DataFrame(data_dict)
    df.to_hdf(
        output_file,
        key="corsika_muons",
        mode="w",
    )

    return


if __name__ == "__main__":
    main()
