"""Sensitivity sweep of MTOM with range and customer count for QBiT and hexarotor architectures."""

import csv
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


def find_crossover(x_vals, y1_vals, y2_vals):
    y1 = np.asarray(y1_vals)
    y2 = np.asarray(y2_vals)
    diff = y1 - y2

    for i in range(len(diff) - 1):
        if diff[i] > 0 and diff[i + 1] < 0:
            x_cross = x_vals[i] - diff[i] * (x_vals[i + 1] - x_vals[i]) / (diff[i + 1] - diff[i])
            return x_cross
    return None


def run_parameter_sweep():
    payload_kg = 5.0
    n_c_values = np.arange(1, 6)
    one_way_ranges_km = np.arange(5, 31, 5)
    total_ranges_km = 2.0 * one_way_ranges_km

    results_qbit = {nc: [] for nc in n_c_values}
    results_hex = {nc: [] for nc in n_c_values}

    for r_km in one_way_ranges_km:
        range_m = r_km * 1000.0
        for n_c in n_c_values:
            try:
                prob_q = build_qbit_problem(payload_kg, range_m, n_c=n_c)
                prob_q.run_driver()
                mtom_q_kg = prob_q.get_val('W_total')[0] / G_QBIT if prob_q.driver.result.success else np.nan
            except Exception:
                mtom_q_kg = np.nan
            results_qbit[n_c].append(mtom_q_kg)

            try:
                prob_h = build_hex_problem(payload_kg, range_m, n_c=n_c)
                prob_h.run_driver()
                mtom_h_kg = prob_h.get_val('W_total')[0] / G_HEX if prob_h.driver.result.success else np.nan
            except Exception:
                mtom_h_kg = np.nan
            results_hex[n_c].append(mtom_h_kg)

    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, 'breakeven_points_mtom_range_nc.csv')
    breakeven_data = []

    for n_c in n_c_values:
        q_vals = np.asarray(results_qbit[n_c])
        h_vals = np.asarray(results_hex[n_c])
        cross_r = find_crossover(total_ranges_km, q_vals, h_vals)

        if cross_r is not None:
            mtom_at_cross = np.interp(cross_r, total_ranges_km, q_vals)
            breakeven_data.append({
                'n_c': n_c,
                'breakeven_mtom_kg': round(float(mtom_at_cross), 2),
                'total_range_km': round(float(cross_r), 2),
            })

    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['n_c', 'breakeven_mtom_kg', 'total_range_km'])
        writer.writeheader()
        writer.writerows(breakeven_data)

    colors = plt.get_cmap('tab10').colors
    fig, ax = plt.subplots(figsize=(8, 8))

    for i, n_c in enumerate(n_c_values):
        q_vals = np.asarray(results_qbit[n_c])
        h_vals = np.asarray(results_hex[n_c])
        ax.plot(total_ranges_km, q_vals, '-', color=colors[i], linewidth=2.0)
        ax.plot(total_ranges_km, h_vals, '--', color=colors[i], linewidth=1.8, alpha=0.8)
        mask = q_vals < h_vals
        ax.fill_between(total_ranges_km, q_vals, h_vals, where=mask, color=colors[i], alpha=0.1, interpolate=True)

    ax.set_title(f'Sizing Sensitivity (Payload Mass: $m_{{pay}} = {payload_kg}$ kg)', fontsize=20, pad=18)
    ax.set_xlabel('Total Mission Range, $R$ [km]', fontsize=16)
    ax.set_ylabel('Maximum Take-off Mass (MTOM) [kg]', fontsize=16)
    ax.set_xticks(total_ranges_km)
    ax.grid(True, linestyle=':', alpha=0.6)

    style_legend = [
        Line2D([0], [0], color='black', linestyle='-', label='QBiT (Transition)', lw=2),
        Line2D([0], [0], color='black', linestyle='--', label='Hexarotor (Multirotor)', lw=2),
    ]
    leg1 = ax.legend(handles=style_legend, loc='upper left', fontsize=12, frameon=True, title='Vehicle Architecture')
    ax.add_artist(leg1)

    count_legend = [
        Line2D([0], [0], color=colors[i], lw=3, label=f'$n_c = {n_c}$')
        for i, n_c in enumerate(n_c_values)
    ]
    ax.legend(handles=count_legend, loc='lower right', fontsize=12, ncol=2, frameon=True, title='Customer Count')

    fig.tight_layout()
    output_path = os.path.join(results_dir, 'mtom_sensitivity_payload_5kg.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    print(f'Plot saved to: {output_path}')
    print(f'CSV saved to: {csv_path}')


if __name__ == '__main__':
    run_parameter_sweep()
