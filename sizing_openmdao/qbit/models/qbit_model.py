import openmdao.api as om

from qbit.groups.physics_group import PhysicsGroup
from qbit.groups.constraints_group import ConstraintsGroup


def build_qbit_model(payload_kg: float,
                   range_m: float,
                   n_c: int = 1) -> om.Group:
    model = om.Group()

    ivc = om.IndepVarComp()
    ivc.add_output('W_payload', val=payload_kg * 9.81, units='N')
    ivc.add_output('R', val=range_m, units='m')
    ivc.add_output('n_c', val=float(n_c))

    ivc.add_output('V_inf', val=33.0, units='m/s')
    ivc.add_output('r', val=0.22, units='m')
    ivc.add_output('J', val=1.3)
    ivc.add_output('S_w', val=0.20, units='m**2')

    model.add_subsystem('ivc', ivc, promotes=['*'])
    model.add_subsystem('physics', PhysicsGroup(), promotes=['*'])
    model.add_subsystem('constraints', ConstraintsGroup(), promotes=['*'])

    return model
