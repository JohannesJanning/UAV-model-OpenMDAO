import numpy as np
import openmdao.api as om
from hexarotor.constants import (
    G, N_ROTOR, BETA_HEX, T_HOVER,
    K_MOTOR, K_ESC, K_ROTOR_A, K_ROTOR_B,
    BATTERY_DENSITY, BATTERY_EFF,
)


class InstalledPowerComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('P_hover', val=400.0, units='W')
        self.add_input('P_cruise', val=250.0, units='W')
        self.add_output('P_inst', val=600.0, units='W')

    def setup_partials(self):
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        Ph = inputs['P_hover'][0]
        Pc = inputs['P_cruise'][0]
        outputs['P_inst'] = 1.5 * (Ph if float(np.real(Ph)) >= float(np.real(Pc)) else Pc)


class EmptyWeightComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('P_inst', val=600.0, units='W')
        self.add_input('r', val=0.25, units='m')
        self.add_input('W_total', val=50.0, units='N')
        self.add_output('W_empty', val=15.0, units='N')

    def setup_partials(self):
        self.declare_partials('W_empty', ['P_inst', 'r', 'W_total'])

    def compute(self, inputs, outputs):
        Pi = inputs['P_inst'][0]
        r = inputs['r'][0]
        W = inputs['W_total'][0]

        W_motor = (K_MOTOR + K_ESC) * Pi * G
        W_rotor = N_ROTOR * (K_ROTOR_A * r**2 - K_ROTOR_B * r) * G
        W_frame = 0.5 * G + BETA_HEX * W

        outputs['W_empty'] = W_motor + W_rotor + W_frame

    def compute_partials(self, inputs, partials):
        r = inputs['r'][0]
        partials['W_empty', 'P_inst'] = (K_MOTOR + K_ESC) * G
        partials['W_empty', 'r'] = N_ROTOR * (2.0 * K_ROTOR_A * r - K_ROTOR_B) * G
        partials['W_empty', 'W_total'] = BETA_HEX


class MissionEnergyComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('P_hover', val=400.0, units='W')
        self.add_input('P_cruise', val=250.0, units='W')
        self.add_input('V_inf', val=18.0, units='m/s')
        self.add_input('R', val=30e3, units='m')
        self.add_input('n_c', val=1.0)
        self.add_output('E_req', val=5e5, units='J')

    def setup_partials(self):
        self.declare_partials('E_req', ['P_hover', 'P_cruise', 'V_inf', 'R', 'n_c'])

    def compute(self, inputs, outputs):
        Ph = inputs['P_hover'][0]
        Pc = inputs['P_cruise'][0]
        V = inputs['V_inf'][0]
        R = inputs['R'][0]
        nc = int(round(float(inputs['n_c'][0])))

        outputs['E_req'] = Ph * (2.0 * (nc + 1) * T_HOVER) + Pc * (R / V)

    def compute_partials(self, inputs, partials):
        Pc = inputs['P_cruise'][0]
        V = inputs['V_inf'][0]
        R = inputs['R'][0]
        Ph = inputs['P_hover'][0]
        nc = int(round(float(inputs['n_c'][0])))

        partials['E_req', 'P_hover'] = 2.0 * (nc + 1) * T_HOVER
        partials['E_req', 'P_cruise'] = R / V
        partials['E_req', 'V_inf'] = -Pc * R / V**2
        partials['E_req', 'R'] = Pc / V
        partials['E_req', 'n_c'] = 2.0 * T_HOVER * Ph


class BatteryWeightComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('E_req', val=5e5, units='J')
        self.add_output('W_battery', val=10.0, units='N')

    def setup_partials(self):
        self.declare_partials('W_battery', 'E_req',
                              val=G / (3600.0 * BATTERY_EFF * BATTERY_DENSITY))

    def compute(self, inputs, outputs):
        outputs['W_battery'] = (inputs['E_req'][0] / 3600.0) / (BATTERY_EFF * BATTERY_DENSITY) * G


class WeightResidualComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('W_total', val=50.0, units='N')
        self.add_input('W_payload', val=29.43, units='N')
        self.add_input('W_battery', val=10.0, units='N')
        self.add_input('W_empty', val=15.0, units='N')
        self.add_output('weight_residual', val=0.0, units='N')

    def setup_partials(self):
        self.declare_partials('weight_residual', 'W_total', val=1.0)
        self.declare_partials('weight_residual', 'W_payload', val=-1.0)
        self.declare_partials('weight_residual', 'W_battery', val=-1.0)
        self.declare_partials('weight_residual', 'W_empty', val=-1.0)

    def compute(self, inputs, outputs):
        outputs['weight_residual'] = (inputs['W_total']
                                      - inputs['W_payload']
                                      - inputs['W_battery']
                                      - inputs['W_empty'])
