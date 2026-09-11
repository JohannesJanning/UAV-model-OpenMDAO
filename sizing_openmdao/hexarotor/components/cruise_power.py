import numpy as np
import openmdao.api as om
from hexarotor.constants import RHO_AIR, ETA_HOVER, N_ROTOR, KAPPA_MAX


class CruisePowerComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('T_cruise', val=5.0, units='N')
        self.add_input('Vi', val=0.5, units='m/s')
        self.add_input('P0', val=20.0, units='W')
        self.add_input('V_inf', val=18.0, units='m/s')
        self.add_input('r', val=0.25, units='m')
        self.add_input('beta', val=0.09, units='rad')
        self.add_output('P_cruise', val=200.0, units='W')

    def setup_partials(self):
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        T = inputs['T_cruise'][0]
        Vi = inputs['Vi'][0]
        P0 = inputs['P0'][0]
        V = inputs['V_inf'][0]
        r = inputs['r'][0]
        beta = inputs['beta'][0]

        A = np.pi * r**2
        kappa_formula = (1.0 / ETA_HOVER
                         - np.sqrt(2.0 * RHO_AIR * A) / T**1.5 * P0)
        kappa = (KAPPA_MAX
                 if float(np.real(kappa_formula)) > KAPPA_MAX
                 else kappa_formula)

        P_per = T * V * np.sin(beta) + kappa * T * Vi + P0
        outputs['P_cruise'] = N_ROTOR * P_per
