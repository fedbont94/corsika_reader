"""
This script creates the submit and sh files for the condor submission
The submit files are created in the output directory in the sub_file directory
"""

import glob
import sys
import argparse
import os
import pathlib
import numpy as np


def __check_args(args):
    """
    Check if the arguments are valid
    """
    if not os.path.isdir(args.input_directory):
        sys.exit("Input directory does not exist!")
    return


def get_args():
    """
    Command line arguments
    """
    p = argparse.ArgumentParser()

    p.add_argument(
        "--input_directory",
        help="Input directory where all the simulations / data are stored",
        # nargs='*',
    )
    p.add_argument(
        "--output_directory",
        help="Output directory",
        type=str,
    )
    p.add_argument(
        "--year",
        help="dataset year",
    )
    p.add_argument(
        "--primary",
        default="",
        type=str,
        help="Primary particle type: gamma, p, He, O, Fe",
    )
    p.add_argument(
        "--energyStart",
        default=0.0,
        type=float,
        help="Starting energy",
    )
    p.add_argument(
        "--energyEnd",
        default=0.0,
        type=float,
        help="Ending energy",
    )
    p.add_argument(
        "--energyCut",
        default=0.0,
        type=float,
        help="Energy cut for muons",
    )

    args = p.parse_args()
    return args


def write_sumtit_sh_file(
    args,
    inputDir,
    energy,
    baseName,
):
    """
    Create the submit and sh files for the condor submission
    Creates the output directory if it does not exist
    """

    # Check if the directory exists, if not, create it
    pathlib.Path(f"{args.output_directory}/sub_file/").mkdir(
        parents=True, exist_ok=True
    )
    pathlib.Path(f"/home/fbontempo/getMuonsFromCorsika/logs_{args.primary}/").mkdir(
        parents=True, exist_ok=True
    )

    with open(f"{args.output_directory}/sub_file/{baseName}.sub", "w") as f:
        f.write(
            ""
            + f"\nexecutable = {args.output_directory}/sub_file/{baseName}.sh"
            + f"\narguments = ''"
            + f"\nlog = /home/fbontempo/getMuonsFromCorsika/logs_{args.primary}/{baseName}.log"
            + f"\noutput = /home/fbontempo/getMuonsFromCorsika/logs_{args.primary}/{baseName}.out"
            + f"\nerror = /home/fbontempo/getMuonsFromCorsika/logs_{args.primary}/{baseName}.err"
            + f"\nrequest_cpus = 1"
            + f"\nrequest_memory = 2 GB"
            + f"\nrequest_disk = 2 GB"
            + f"\nqueue 1"
        )
    with open(f"{args.output_directory}/sub_file/{baseName}.sh", "w") as f:
        f.write(
            ""
            + r"#!/bin/bash"
            + "\nENV=/data/user/mweyrauch/PhD/software/surface-array/build/env-shell.sh"
            + "\nPYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3"
            + "\nSCRIPT=/home/fbontempo/getMuonsFromCorsika/readCorsikaMuons.py"
            + "\neval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`"
            + "\n$ENV python $SCRIPT"
            + f" --inputDir {inputDir}"
            + f" --outputDir {args.output_directory}"
            + f" --energy {energy}"
            + f" --energyCut {args.energyCut}"
            # +   f"\nrm {args.output_directory}/sub_file/{baseName}.sh {args.output_directory}/sub_file/{baseName}.sub"
        )

    # Makes sh executable and submits the job
    os.system(f"chmod +x {args.output_directory}/sub_file/{baseName}.sh")
    os.system(f"condor_submit {args.output_directory}/sub_file/{baseName}.sub")
    return


def main(args):
    """
    Checks the arguments, gets the input files and creates the submit and sh files
    """
    __check_args(args)

    energies = np.around(
        np.arange(
            args.energyStart,
            args.energyEnd,
            0.1,
        ),
        decimals=1,
    )
    for energy in energies:
        write_sumtit_sh_file(
            args=args,
            inputDir=f"{args.input_directory}/",
            energy=energy,
            baseName=f"{args.primary}{args.year}E{energy}",
        )


if __name__ == "__main__":
    main(args=get_args())

    print("-------------------- Program finished --------------------")
