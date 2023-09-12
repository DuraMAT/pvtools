import pvlib

__version__ = '0.0.7'
contact_email = 'pvtools.duramat@gmail.com'

# List of modules in the CEC database.
cec_modules = pvlib.pvsystem.retrieve_sam('CeCMod')
cec_module_dropdown_list = []
for m in list(cec_modules.keys()):
    cec_module_dropdown_list.append(
        {'label': m.replace('_', ' '), 'value': m})