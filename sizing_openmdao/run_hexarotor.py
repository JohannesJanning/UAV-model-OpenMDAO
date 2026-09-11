from __future__ import annotations
import warnings
from dataclasses import dataclass

import numpy as np
import openmdao.api as om

om.config_reports = False

from hexarotor.models.hexarotor_model import build_hexarotor_model
from hexarotor.constants import (
    BATTERY_EFF,
    G,
    W_TOTAL_BOUNDS,
    V_INF_BOUNDS,
    R_BOUNDS,
    MU_BOUNDS,
    DL_MAX,
    BL_MAX,
)

PAYLOAD_KG = 3.0
RANGE_M = 15000.0 # one direction
N_C = 1


@dataclass
class HexarotorResult:
    W_total: float
    W_battery: float
    W_empty: float
    P_hover: float
    P_cruise: float
    V_inf: float
    r: float
    mu: float
    beta_deg: float
    E_req: float
    converged: bool

    def summary(self) -> str:
        lines = [
            f"  MTOM          : {self.W_total / G:7.3f} kg  ({self.W_total:.1f} N)",
            f"  Battery mass  : {self.W_battery / G:7.3f} kg",
            f"  Empty mass    : {self.W_empty / G:7.3f} kg",
            f"  Cruise speed  : {self.V_inf:7.2f} m/s",
            f"  Rotor radius  : {self.r:7.4f} m",
            f"  Adv. ratio μ  : {self.mu:7.4f}",
            f"  Shaft tilt β  : {self.beta_deg:7.2f}°",
            f"  P_hover       : {self.P_hover:8.1f} W",
            f"  P_cruise      : {self.P_cruise:8.1f} W",
            f"  E_required    : {self.E_req / 3600:.3f} Wh",
            f"  Converged     : {self.converged}",
        ]
        return "\n".join(lines)


def build_problem(payload_kg: float = PAYLOAD_KG,
                 range_m: float = RANGE_M,
                 n_c: int = N_C) -> om.Problem:
    prob = om.Problem(reports=None)
    prob.model = build_hexarotor_model(payload_kg, range_m, n_c)

    prob.model.set_input_defaults('W_total', val=5.0 * G, units='N')

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['tol'] = 1e-9
    prob.driver.options['maxiter'] = 2000

    prob.model.add_design_var('W_total', lower=W_TOTAL_BOUNDS[0], upper=W_TOTAL_BOUNDS[1])
    prob.model.add_design_var('V_inf', lower=V_INF_BOUNDS[0], upper=V_INF_BOUNDS[1])
    prob.model.add_design_var('r', lower=R_BOUNDS[0], upper=R_BOUNDS[1])
    prob.model.add_design_var('mu', lower=MU_BOUNDS[0], upper=MU_BOUNDS[1])

    prob.model.add_objective('W_total')
    prob.model.add_constraint('weight_residual', equals=0.0)
    prob.model.add_constraint('disk_loading', upper=DL_MAX)
    prob.model.add_constraint('blade_loading', upper=BL_MAX)

    prob.setup()
    prob.set_val('W_total', 5.0 * G)
    return prob


def solve_hexarotor(payload_kg: float = PAYLOAD_KG,
                   range_m: float = RANGE_M,
                   n_c: int = N_C,
                   verbose: bool = True) -> HexarotorResult:
    prob = build_problem(payload_kg=payload_kg, range_m=range_m, n_c=n_c)

    if verbose:
        print('=' * 60)
        print('Hexarotor sizing model')
        print(f'payload = {payload_kg:.2f} kg')
        print(f'range = {range_m:.0f} m')
        print(f'nodes = {n_c}')
        print('=' * 60)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        prob.run_driver()

    W = float(prob.get_val('W_total')[0])
    Ph = float(prob.get_val('P_hover')[0] / BATTERY_EFF)
    Pc = float(prob.get_val('P_cruise')[0] / BATTERY_EFF)
    V = float(prob.get_val('V_inf')[0])
    r = float(prob.get_val('r')[0])
    mu = float(prob.get_val('mu')[0])
    beta = float(prob.get_val('beta')[0])
    Wb = float(prob.get_val('W_battery')[0])
    We = float(prob.get_val('W_empty')[0])
    E = float(prob.get_val('E_req')[0])

    converged = getattr(getattr(prob.driver, 'result', None), 'success', True)

    result = HexarotorResult(
        W_total=W,
        W_battery=Wb,
        W_empty=We,
        P_hover=Ph,
        P_cruise=Pc,
        V_inf=V,
        r=r,
        mu=mu,
        beta_deg=np.degrees(beta),
        E_req=E,
        converged=converged,
    )

    if verbose:
        print(result.summary())
        print('=' * 60)

    return result


if __name__ == '__main__':
    result = solve_hexarotor(payload_kg=PAYLOAD_KG, range_m=RANGE_M, n_c=N_C, verbose=True)
    mtom_kg = result.W_total / G

    assert 0.5 <= mtom_kg <= 50.0, f'MTOM {mtom_kg:.3f} kg outside [0.5, 50.0]'
    assert result.converged
    print(f'\nValidation passed: MTOM = {mtom_kg:.3f} kg ✓')
