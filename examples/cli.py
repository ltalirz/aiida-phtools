#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
import os
import click


@click.command('cli')
@click.argument('codelabel')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def main(codelabel, submit):
    """Command line interface for testing and submitting calculations.

    Usage: ./cli.py CODENAME COMPUTER_NAME
    
    CODENAME       from "verdi code setup"

    COMPUTER_NAME  from "verdi computer setup"

    This script extends submit.py, adding flexibility in the selected code/computer.
    """
    code = Code.get_from_string(codelabel)

    # set up calculation
    calc = code.new_calc()
    calc.label = "aiida_phtools example calculation"
    calc.description = "Computes proper pore surface as needed for persistence homology calculation"
    calc.set_max_wallclock_seconds(1 * 60)
    calc.set_withmpi(False)
    calc.set_resources({"num_machines": 1})

    # Prepare input parameters
    PoreSurfaceParameters = DataFactory('phtools.surface')
    d = {
        'accessible_surface_area': 300.0,
        'target_volume': 40e3,
        'sampling_method': 'random',
    }
    parameters = PoreSurfaceParameters(dict=d)
    calc.use_parameters(parameters)

    SinglefileData = DataFactory('singlefile')
    this_dir = os.path.dirname(os.path.realpath(__file__))
    structure = SinglefileData(file=os.path.join(this_dir, 'HKUST-1.cssr'))
    calc.use_structure(structure)

    surface_sample = SinglefileData(file=os.path.join(this_dir, 'HKUST-1.vsa'))
    calc.use_surface_sample(surface_sample)

    if submit:
        calc.store_all()
        calc.submit()
        print("submitted calculation; calc=Calculation(uuid='{}') # ID={}"\
                .format(calc.uuid,calc.dbnode.pk))
    else:
        subfolder, script_filename = calc.submit_test()
        path = os.path.relpath(subfolder.abspath)
        print("submission test successful")
        print("Find remote folder in {}".format(path))
        print("In order to actually submit, add '--submit'")


if __name__ == '__main__':
    main()
