import openmdao.api as om


class WeightResidualComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('W_total', val=60.0, units='N')
        self.add_input('W_payload', val=29.43, units='N')
        self.add_input('W_battery', val=10.0, units='N')
        self.add_input('W_empty', val=20.0, units='N')
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
