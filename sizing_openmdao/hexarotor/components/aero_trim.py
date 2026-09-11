import numpy as np
import openmdao.api as om
from hexarotor.constants import RHO_AIR, N_ROTOR, SIGMA, CD0_ROTOR


def _body_drag(V, r, beta):
    rb = 0.58 * r
    Sb = rb * 2.5 * 2.0 * rb
    CDb = 0.1 + 0.2 * np.cos(beta)**3
    return 0.5 * RHO_AIR * V**2 * Sb * CDb


def _solve_beta(W, V, r, tol=1e-12, maxiter=200):
    beta = np.arctan(_body_drag(V, r, np.radians(5.0)) / W)
    for _ in range(maxiter):
        Db = _body_drag(V, r, beta)
        f = beta - np.arctan(Db / W)
        rb = 0.58 * r
        Sb = rb * 2.5 * 2.0 * rb
        dCDb = 0.2 * (-3.0 * np.cos(beta)**2 * np.sin(beta))
        dDb = 0.5 * RHO_AIR * V**2 * Sb * dCDb
        df = 1.0 - (W / (W**2 + Db**2)) * dDb
        step = f / df
        beta = beta - step
        if np.abs(step) < tol:
            break
    return beta


def _solve_lambda(mu, CT, beta, tol=1e-12, maxiter=200):
    lam = CT / (2.0 * np.sqrt(mu**2 + (CT / 2.0)**2))
    for _ in range(maxiter):
        g = np.sqrt(mu**2 + lam**2)
        f = lam - mu * np.tan(beta) - CT / (2.0 * g)
        df = 1.0 + CT * lam / (2.0 * g**3)
        step = f / df
        lam = lam - step
        if np.abs(step) < tol:
            break
    return lam


class AerodynamicTrimComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('W_total', val=50.0, units='N')
        self.add_input('r', val=0.25, units='m')
        self.add_input('V_inf', val=18.0, units='m/s')
        self.add_input('mu', val=0.30)

        self.add_output('T_cruise', val=5.0, units='N')
        self.add_output('beta', val=0.09, units='rad')
        self.add_output('mu_c', val=0.30)
        self.add_output('CT', val=0.01)
        self.add_output('lam', val=0.3)
        self.add_output('Vi', val=0.5, units='m/s')
        self.add_output('P0', val=20.0, units='W')

    def setup_partials(self):
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        W = inputs['W_total'][0]
        r = inputs['r'][0]
        V = inputs['V_inf'][0]
        mu = inputs['mu'][0]

        beta = _solve_beta(W, V, r)
        Db = _body_drag(V, r, beta)
        T = np.sqrt(W**2 + Db**2) / N_ROTOR

        Om = V * np.cos(beta) / (mu * r)
        A = np.pi * r**2

        CT = T / (RHO_AIR * A * (Om * r)**2)
        mu_c = V * np.cos(beta) / (Om * r)

        lam = _solve_lambda(mu_c, CT, beta)

        Vi = lam * Om * r - V * np.sin(beta)

        P0 = (SIGMA * CD0_ROTOR / 8.0
              * (1.0 + 4.65 * mu_c**2)
              * RHO_AIR * A * (Om * r)**3)

        outputs['T_cruise'] = T
        outputs['beta'] = beta
        outputs['mu_c'] = mu_c
        outputs['CT'] = CT
        outputs['lam'] = lam
        outputs['Vi'] = Vi
        outputs['P0'] = P0
