from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from hexarotor.constants import G
from run_hexarotor import solve_hexarotor
from run_qbit import solve_qbit


PAYLOAD_KG = 3.0
RANGES_KM = (10, 20, 30, 40, 50, 60)

HEXAROTOR_COLOR = "#1565c0"
QBIT_COLOR = "#ef6c00"

OUTPUT_DIRECTORY = Path(__file__).with_name("comparison_results")
PLOT_PATH = OUTPUT_DIRECTORY / "power_comparison.png"
DESIGN_COMPARISON_PLOT_PATH = OUTPUT_DIRECTORY / "design_comparison.png"
CSV_PATH = OUTPUT_DIRECTORY / "design_comparison.csv"


def collect_results() -> list[dict[str, float | str]]:
    results: list[dict[str, float | str]] = []

    for total_range_km in RANGES_KM:
        total_range_m = total_range_km * 1_000.0
        print(f"Running models for total range R = {total_range_km} km...")

        hexarotor = solve_hexarotor(
            payload_kg=PAYLOAD_KG,
            range_m=total_range_m,
            n_c=1,
            verbose=False,
        )
        qbit = solve_qbit(
            payload_kg=PAYLOAD_KG,
            range_m=total_range_m,
            n_c=1,
            verbose=False,
        )

        results.extend(
            [
                {
                    "design": "Hexarotor",
                    "range_km": float(total_range_km),
                    "mtom_kg": hexarotor.W_total / G,
                    "energy_wh": hexarotor.E_req / 3600.0,
                    "cruise_speed_m_s": hexarotor.V_inf,
                    "power_cruise_kw": hexarotor.P_cruise / 1000.0,
                    "power_hover_kw": hexarotor.P_hover / 1000.0,
                    "rotor_radius_m": hexarotor.r,
                },
                {
                    "design": "QBiT",
                    "range_km": float(total_range_km),
                    "mtom_kg": qbit.W_total / G,
                    "energy_wh": qbit.E_req / 3600.0,
                    "cruise_speed_m_s": qbit.V_inf,
                    "power_cruise_kw": qbit.P_cruise / 1000.0,
                    "power_hover_kw": qbit.P_hover / 1000.0,
                    "rotor_radius_m": qbit.r,
                },
            ]
        )

    return results


def save_results(results: list[dict[str, float | str]]) -> None:
    fieldnames = list(results[0])
    with CSV_PATH.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def plot_results(results: list[dict[str, float | str]]) -> None:
    hexarotor = [row for row in results if row["design"] == "Hexarotor"]
    qbit = [row for row in results if row["design"] == "QBiT"]

    ranges = [float(row["range_km"]) for row in hexarotor]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "font.size": 13,
            "axes.titlesize": 15,
            "axes.labelsize": 14,
            "axes.linewidth": 1.1,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
        }
    )

    figure, power_axis = plt.subplots(
        1,
        1,
        figsize=(8, 5),
        constrained_layout=True,
    )
    power_axis.set_title(f"Power comparison, {PAYLOAD_KG:.0f} kg payload")
    power_axis.plot(
        ranges,
        [float(row["power_cruise_kw"]) for row in hexarotor],
        color=HEXAROTOR_COLOR,
        linewidth=2.2,
        label="Hexarotor cruise",
    )
    power_axis.plot(
        ranges,
        [float(row["power_cruise_kw"]) for row in qbit],
        color=QBIT_COLOR,
        linewidth=2.2,
        label="QBiT cruise",
    )
    power_axis.plot(
        ranges,
        [float(row["power_hover_kw"]) for row in hexarotor],
        color=HEXAROTOR_COLOR,
        linewidth=2.0,
        linestyle="--",
        label="Hexarotor hover",
    )
    power_axis.plot(
        ranges,
        [float(row["power_hover_kw"]) for row in qbit],
        color=QBIT_COLOR,
        linewidth=2.0,
        linestyle="--",
        label="QBiT hover",
    )
    power_axis.set_xlabel("Total closed-route distance, R (km)")
    power_axis.set_ylabel("Power (kW)")
    power_axis.set_xlim(9, 61)
    power_axis.set_ylim(0.2, 1.15)
    power_axis.set_xticks(RANGES_KM)
    power_axis.grid(True, alpha=0.25)
    power_axis.legend(frameon=False, fontsize=11, loc="upper left", ncol=2)
    figure.savefig(PLOT_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)

    figure, axes = plt.subplots(3, 2, figsize=(9, 9), constrained_layout=True)
    figure.suptitle(f"UAV design comparison, {PAYLOAD_KG:.0f} kg payload")
    comparison_axes = (
        (axes[0, 0], "mtom_kg", "MTOM (kg)"),
        (axes[0, 1], "energy_wh", "Energy (Wh)"),
        (axes[1, 0], "cruise_speed_m_s", "Cruise speed (m/s)"),
        (axes[1, 1], "rotor_radius_m", "Rotor radius (m)"),
    )

    for axis, field, label in comparison_axes:
        axis.plot(ranges, [float(row[field]) for row in hexarotor], color=HEXAROTOR_COLOR, linewidth=2.2, label="Hexarotor")
        axis.plot(ranges, [float(row[field]) for row in qbit], color=QBIT_COLOR, linewidth=2.2, label="QBiT")
        axis.set_xlabel("Total closed-route distance, R (km)")
        axis.set_ylabel(label)
        axis.set_xlim(9, 61)
        axis.set_xticks(RANGES_KM)
        axis.grid(True, alpha=0.25)
        axis.legend(frameon=False, fontsize=9, loc="upper left")

    power_axis = axes[2, 0]
    power_axis.plot(ranges, [float(row["power_cruise_kw"]) for row in hexarotor], color=HEXAROTOR_COLOR, linewidth=2.2, label="Hexarotor cruise")
    power_axis.plot(ranges, [float(row["power_cruise_kw"]) for row in qbit], color=QBIT_COLOR, linewidth=2.2, label="QBiT cruise")
    power_axis.plot(ranges, [float(row["power_hover_kw"]) for row in hexarotor], color=HEXAROTOR_COLOR, linewidth=2.0, linestyle="--", label="Hexarotor hover")
    power_axis.plot(ranges, [float(row["power_hover_kw"]) for row in qbit], color=QBIT_COLOR, linewidth=2.0, linestyle="--", label="QBiT hover")
    power_axis.set_xlabel("Total closed-route distance, R (km)")
    power_axis.set_ylabel("Power (kW)")
    power_axis.set_xlim(9, 61)
    power_axis.set_xticks(RANGES_KM)
    power_axis.grid(True, alpha=0.25)
    power_axis.legend(frameon=False, fontsize=9, loc="upper left")
    axes[2, 1].set_visible(False)
    figure.savefig(DESIGN_COMPARISON_PLOT_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    results = collect_results()
    save_results(results)
    plot_results(results)
    print(f"Saved plot to {PLOT_PATH}")
    print(f"Saved plot to {DESIGN_COMPARISON_PLOT_PATH}")
    print(f"Saved data to {CSV_PATH}")


if __name__ == "__main__":
    main()