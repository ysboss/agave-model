import input_params
import jetlag_conf

import pprint
pp = pprint.PrettyPrinter()

def observe_title(change):
    if change["name"] == "value":
        input_params.set('title',change['new'])

class observe_middleware:
    def __init__(self,machines):
        self.machines = machines
    def __call__(self,change):
        if change["name"] == "value":
            input_params.set('middleware',change['new'])
            middleware_value=input_params.get('middleware')
            machinesValue = input_params.get('machine_'+middleware_value)
            jetlag_conf.gen_data()
            self.machines.options = jetlag_conf.machines_options
            if machinesValue in self.machines.options:
                self.machines.value = machinesValue
