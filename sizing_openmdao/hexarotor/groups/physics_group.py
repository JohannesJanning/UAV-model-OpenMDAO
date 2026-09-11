import openmdao.api as om

from hexarotor.components.hover_power import HoverPowerComp
from hexarotor.components.aero_trim import AerodynamicTrimComp
from hexarotor.components.cruise_power import CruisePowerComp
from hexarotor.components.sizing_comps import (InstalledPowerComp,
                                                EmptyWeightComp,
                                                MissionEnergyComp,
                                                BatteryWeightComp,
                                                WeightResidualComp)


class PhysicsGroup(om.Group):

    def setup(self):
        self.add_subsystem('hover', HoverPowerComp(), promotes=['*'])
        self.add_subsystem('trim', AerodynamicTrimComp(), promotes=['*'])
        self.add_subsystem('cruise', CruisePowerComp(), promotes=['*'])
        self.add_subsystem('installed', InstalledPowerComp(), promotes=['*'])
        self.add_subsystem('empty', EmptyWeightComp(), promotes=['*'])
        self.add_subsystem('energy', MissionEnergyComp(), promotes=['*'])
        self.add_subsystem('battery', BatteryWeightComp(), promotes=['*'])
        self.add_subsystem('balance', WeightResidualComp(), promotes=['*'])
