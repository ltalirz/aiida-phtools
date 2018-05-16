"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""
from voluptuous import Schema, Optional
from aiida.orm.data.parameter import ParameterData

cmdline_parameters = {
    'accessible_surface_area': float,
    'output_surface': Optional(str, default='out.sa'),
    'sampling_density': Optional(float, default=0.5),
    'target_volume': Optional(float, default=0.0),
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
            super(PoreSurfaceParameters, self).__init__(dict=dict, **kwargs)
            dict = self.validate(dict)

    def validate(self, parameters_dict):
        """validate parameters"""
        return PoreSurfaceParameters.schema(parameters_dict, required=True)

    def cmdline_params(self, structure_file_name, surface_sample_file_name):
        """Synthesize command line parameters

        e.g. [ ['struct.cssr'], ['struct.sa'], [2.4]]
        """
        parameters = []

        parameters += [structure_file_name]
        parameters += [surface_sample_file_name]

        pm_dict = self.get_dict()

        # order matters here!
        for key in [
                'accessible_surface_area', 'sampling_density',
                'output_surface', 'target_volume'
        ]:
            parameters.append(pm_dict[key])

        return map(str, parameters)

    @property
    def output_files(self):
        """Return list of output files to be retrieved"""
        output_list = []

        pm_dict = self.get_dict()
        output_list.append(pm_dict['output_file'])
        if pm_dict['target_volume'] != 0.0:
            output_list.append(pm_dict['output_file'] + str(".cell"))

        return output_list

    @property
    def output_keys(self):
        """Return list of output link names"""
        output_keys = []

        pm_dict = self.get_dict()
        output_keys.append('surface_sample')
        if pm_dict['target_volume'] != 0.0:
            output_keys.append('surface_cell')

        return self.output_keys
