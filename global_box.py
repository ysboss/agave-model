import imp
if 'input_params' in globals():
    imp.reload(input_params)
else:
    import input_params

import pprint
pp = pprint.PrettyPrinter()

def observe_title(change):
    if change["name"] == "value":
        pp.pprint(change)
        input_params.set('title',change['new'])

def observe_middleware(change):
    if change["name"] == "value":
        pp.pprint(change)
        input_params.set('middleware',change['new'])
