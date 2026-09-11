"""Sensitivity sweep comparing QBiT and hexarotor MTOM across mission range and customer count."""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
from matplotlib.lines import Line2D

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

om.config_reports = False

from qbit.constants import G as G_QBIT
from hexarotor.constants import G as G_HEX
from run_qbit import build_problem as build_qbit_problem
from run_hexarotor import build_problem as build_hex_problem


def run_parameter_sweep():
    payload_kg = 3.0
    n_c_values = np.arange(1, 6)
    ranges_km = [5, 10, 15, 20, 25, 30]

    results_qbit = {r_km: [] for r_km in ranges_km}
    results_hex = {r_km: [] for r_km in ranges_km}

    for r_km in ranges_km:
        range_m = r_km * 1000.0
        for n_c in n_c_values:
            try:
                prob_q = build_qbit_problem(payload_kg, range_m, n_c=n_c)
                prob_q.run_driver()
                mtom_q_kg = prob_q.get_val('W_total')[0] / G_QBIT if prob_q.driver.result.success else np.nan
            except Exception:
                mtom_q_kg = np.nan
            results_qbit[r_km].append(mtom_q_kg)

            try:
                prob_h = build_hex_problem(payload_kg, range_m, n_c=n_c)
                prob_h.run_driver()
                mtom_h_kg = prob_h.get_val('W_total')[0] / G_HEX if prob_h.driver.result.success else np.nan
            except Exception:
                mtom_h_kg = np.nan
            results_hex[r_km].append(mtom_h_kg)

    colors = plt.get_cmap('tab10').colors
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, r_km in enumerate(ranges_km):
        q_vals = np.array(results_qbit[r_km])
        h_vals = np.array(results_hex[r_km])
        ax.plot(n_c_values, q_vals, 'o-', color=colors[i], linewidth=1.8, markersize=6)
        ax.plot(n_c_values, h_vals, 's--', color=colors[i], linewidth=1.8, markersize=5)

        mask = q_vals < h_vals
        ax.fill_between(n_c_values, q_vals, h_vals, where=mask, color=colors[i], alpha=0.08, interpolate=True)

    ax.set_title(f'Sizing Sensitivity (Payload Mass: $m_{{pay}} = {payload_kg}$ kg)', fontsize=20, pad=12)
    ax.set_xlabel('Customer Count, $n_c$', fontsize=16)
    ax.set_ylabel('MTOM [kg]', fontsize=16)
    ax.set_xticks(n_c_values)
    ax.grid(True, linestyle='--', alpha=0.6)

    legend_lines = [
        Line2D([0], [0], color='black', linestyle='-', marker='o', label='QBiT (Transition)', lw=2),
        Line2D([0], [0], color='black', linestyle='--', marker='s', label='Hexarotor (Multirotor)', lw=2),
    ]
    leg1 = ax.legend(handles=legend_lines, title='Vehicle Architecture', loc='upper left', frameon=True)
    ax.add_artist(leg1)

    range_legend = [
        Line2D([0], [0], color=colors[i], lw=2, label=f'{r_km} km')
        for i, r_km in enumerate(ranges_km)
    ]
    ax.legend(handles=range_legend, title='Mission Range', loc='upper right', frameon=True, bbox_to_anchor=(1.0, 0.0))

    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, 'mtom_sensitivity_payload_3kg.png')
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    print(f'Output saved to: {output_path}')


if __name__ == '__main__':
    run_parameter_sweep()
