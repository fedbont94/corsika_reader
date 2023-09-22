#!/usr/bin/env python3

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_args():
    parser = argparse.ArgumentParser(description="Plot data from a file")
    parser.add_argument("-i", "--inputDir", help="Input folder", required=True)
    parser.add_argument("-o", "--outputDir", help="Output folder", required=True)
    parser.add_argument("-y", "--year", help="Year of the simulation", required=True)
    parser.add_argument(
        "-z", "--zenith_cut", help="Zenith angle cut in degrees", required=True
    )
    return parser.parse_args()


def read_data(path):
    """
    Read data from the input folder and return a dictionary with the data
    keys for each data file are:
    ['primary', 'energy', 'x', 'y', 'zenith', 'azimuth', 'total_muons', 'muons_above_Ecut']
    """

    data = {}
    for file in sorted(os.listdir(path)):
        if file.endswith(".hdf5"):
            print(f"Reading file {file}")
            df = pd.read_hdf(f"{path}/{file}")
            data[float(file[:3])] = df
    return data


def get_fraction_of_muons(data, args):
    fraction = {}
    energies = list(data.keys())
    for energy in energies:
        # Get the zenith angle cut. below 38 degrees
        zenith_cut = data[energy]["zenith"] < np.deg2rad(float(args.zenith_cut))
        # Get the fraction of muons that reach the in-ice
        fraction[energy] = (
            np.sum(data[energy]["muons_above_Ecut"][zenith_cut] > 0)
            / data[energy]["total_muons"][zenith_cut].shape[0]
        )

    return fraction


def plot_data(fractionOfMuons, args):
    print("Plotting data")
    plt.figure(figsize=(10, 7))
    plt.rcParams.update({"font.size": 16})
    colors = {
        "proton": "red",
        "gamma": "purple",
    }

    # Make sure they have the same energies. Otherwise ratio will be wrong
    gamma_energies = set(fractionOfMuons["gamma"].keys())
    proton_energies = set(fractionOfMuons["proton"].keys())
    energies = gamma_energies.intersection(proton_energies)

    ratio_values = []
    energy_values = []

    # Must sort the energies
    for energy in sorted(energies):
        proton_value = fractionOfMuons["proton"].get(energy)
        gamma_value = fractionOfMuons["gamma"].get(energy)

        if proton_value is not None and gamma_value is not None and gamma_value != 0:
            ratio_values.append(proton_value / gamma_value)
            energy_values.append(energy)

    fig, ax1 = plt.subplots(figsize=(10, 7))
    # Plot the ratio on the right axis
    # ax2 = ax1.twinx()

    # Plot the fraction of muons on the left axis
    for primary in fractionOfMuons.keys():
        ax1.plot(
            fractionOfMuons[primary].keys(),
            fractionOfMuons[primary].values(),
            "o-",
            label=primary,
            linewidth=2,
            markersize=5,
            color=colors[primary],
        )

    ax1.set_xlabel("log$_{10}$(Energy/GeV)")
    ax1.set_ylabel("Fraction of events", color="k")
    ax1.tick_params(axis="y", labelcolor="k")
    ax1.legend(loc="lower right")  # (loc="lower left")  #
    ax1.grid()
    # Add the IceCube preliminary label
    ax1.text(
        0.01,
        0.99,
        "IceCube Preliminary",
        c="r",
        transform=ax1.transAxes,
        fontsize=16,
        verticalalignment="top",
    )

    # Plot the ratio of proton/gamma on the right axis
    # ax2.plot(
    #     energy_values,
    #     ratio_values,
    #     "o-",
    #     label="Proton/Gamma",
    #     linewidth=2,
    #     markersize=5,
    #     color="blue",
    # )
    # ax2.set_xlabel("log$_{10}$(Energy/GeV)")
    # ax2.set_ylabel("Ratio of Proton/Gamma", color="b")
    # ax2.tick_params(axis="y", labelcolor="b")

    plt.title(
        f"Fraction of events with high energy muons \nreaching the in-ice detector $\\theta$<{args.zenith_cut}$^\circ$"
    )

    plt.savefig(
        f"{args.outputDir}/proton_gamma_ratio_{args.year}.png", bbox_inches="tight"
    )
    plt.close()


def main(args):
    data_paths = {
        "gamma": "/data/user/fbontempo/corsikaMuons/gamma/22334/",
        "proton": "/data/user/fbontempo/corsikaMuons/proton/22335/",
    }

    gamma = read_data(path=data_paths["gamma"])
    proton = read_data(path=data_paths["proton"])

    fractionOfMuons = {
        "gamma": get_fraction_of_muons(data=gamma, args=args),
        "proton": get_fraction_of_muons(data=proton, args=args),
    }

    plot_data(fractionOfMuons=fractionOfMuons, args=args)


if __name__ == "__main__":
    main(args=get_args())
    print("-------------------- Program finished --------------------")
