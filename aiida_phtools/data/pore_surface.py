"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""
from voluptuous import Schema, Optional, Required, Any
from aiida.orm.data.parameter import ParameterData

sampling_methods = {
    'random': 1,
    'max_min': 2,
    'grid': 3,
    'epsilon_net': 4,
}

cmdline_parameters = {
    Required('accessible_surface_area'): float,
    Optional('sampling_density', default=0.5): float,
    Optional('output_surface', default='out.vsa'): str,
    Optional('target_volume', default=0.0): float,
    Optional('sampling_method', default=2): Any(*sampling_methods.keys()),
    Optional('cubic_target', default=1): int,
}


class PoreSurfaceParameters(ParameterData):
    """
    Input parameters for surface calculation.
    """
    schema = Schema(cmdline_parameters)

    # pylint: disable=redefined-builtin, too-many-function-args
    def __init__(self, dict=None, **kwargs):
        """
        Constructor for the data class

        Usage: ``PoreSurfaceParameters(dict={'cssr': True})``

        .. note:: As of 2017-09, the constructor must also support a single dbnode
          argument (to reconstruct the object from a database node).
          For this reason, positional arguments are not allowed.
        """
        if 'dbnode' in kwargs:
            super(PoreSurfaceParameters, self).__init__(**kwargs)
        else:
            # set dictionary of ParameterData
            dict = self.validate(dict)
            super(PoreSurfaceParameters, self).__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """validate parameters"""
        return PoreSurfaceParameters.schema(parameters_dict)

    def cmdline_params(self, structure_file_name, surface_sample_file_name):
        """Synthesize command line parameters

        e.g. [ ['struct.cssr'], ['struct.vsa'], [2.4]]
        """
        parameters = []

        parameters += [structure_file_name]
        parameters += [surface_sample_file_name]

        pm_dict = self.get_dict()

        # replace sampling method string by number
        pm_dict['sampling_method'] = sampling_methods[pm_dict[
            'sampling_method']]

        # order matters here!
        for key in [
                'accessible_surface_area',
                'sampling_density',
                'output_surface',
                'target_volume',
                'sampling_method',
                'cubic_target',
        ]:
            parameters.append(pm_dict[key])

        return map(str, parameters)

    @property
    def output_files(self):
        """Return list of output files to be retrieved"""
        output_list = []

        pm_dict = self.get_dict()
        output_list.append(pm_dict['output_surface'])
        if pm_dict['target_volume'] != 0.0:
            output_list.append(pm_dict['output_surface'] + str(".cell"))

        return output_list

    @property
    def output_links(self):
        """Return list of output link names"""
        output_links = []

        pm_dict = self.get_dict()
        output_links.append('surface_sample')
        if pm_dict['target_volume'] != 0.0:
            output_links.append('cell')

        return output_links
