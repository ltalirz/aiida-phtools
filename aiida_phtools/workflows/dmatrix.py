"""
Distance matrix work chain.
"""
from aiida.orm import DataFactory, CalculationFactory
from aiida.orm.code import Code
#from aiida.orm.querybuilder import QueryBuilder

from aiida.orm.data.cif import CifData
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.singlefile import SinglefileData
#from aiida.orm.data.base import Int, Float, Str

from aiida.work.workchain import WorkChain, ToContext, Outputs
from aiida.work.run import submit
from aiida.work.workfunction import workfunction


class DistanceMatrixWorkChain(WorkChain):

    default_options = {
        "resources": {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        },
        "max_wallclock_seconds": 60 * 3,
        "withmpi": False,
    }

    # =========================================================================

    @classmethod
    def define(cls, spec):
        super(DistanceMatrixWorkChain, cls).define(spec)

        spec.input("zeopp_code", valid_type=Code)
        spec.input("distance_matrix_code", valid_type=Code)
        spec.input("pore_surface_code", valid_type=Code)
        spec.input("rips_code", valid_type=Code)
        spec.input("structure", valid_type=CifData)
        spec.input(
            "parameters",
            valid_type=ParameterData,
            default=ParameterData(dict={}),
            required=False)

        spec.outline(
            cls.run_zeopp,
            cls.run_pore_surface,
            cls.run_distance_matrix,
            cls.run_rips_complex,
            cls.run_finish,
        )

        spec.output('barcode', valid_type=SinglefileData)
        spec.output('pore_surface', valid_type=SinglefileData)

    # =========================================================================

    def run_zeopp(self):

        self.report("Running workchain for structure {}".format(
            self.inputs.structure.filename))

        label = "zeopp"
        inputs = {}
        inputs['_label'] = label
        inputs['_description'] = "Sampling accessible pore surface with zeo++"
        inputs['code'] = self.inputs.zeopp_code
        inputs['structure'] = self.inputs.structure

        NetworkParameters = DataFactory('zeopp.parameters')
        network_dict = {
            'cssr': True,
            'ha': True,
            'vsa': [1.8, 1.8, 1000],
            'sa': [1.8, 1.8, 1000],
        }
        inputs['parameters'] = NetworkParameters(dict=network_dict)
        inputs['_options'] = self.default_options

        NetworkCalculation = CalculationFactory('zeopp.network')
        future = submit(NetworkCalculation.process(), **inputs)
        self.report(
            "pk: {} | Submitted zeo++ calculation for structure {}".format(
                future.pid, self.inputs.structure.filename))

        return ToContext(**{label: Outputs(future)})

    # =========================================================================

    def run_pore_surface(self):

        zeopp_out = self.ctx.zeopp

        label = "pore_surface"
        inputs = {}
        inputs['_label'] = label
        inputs[
            '_description'] = "Subsampling pore surface & formation of supercell"
        inputs['code'] = self.inputs.pore_surface_code
        inputs['parameters'] = get_pore_surface_parameters(
            zeopp_out['surface_area_sa'])
        inputs['surface_sample'] = zeopp_out['surface_sample_vsa']
        inputs['structure'] = zeopp_out['structure_cssr']
        inputs['_options'] = self.default_options

        PoreSurfaceCalculation = CalculationFactory('phtools.surface')
        future = submit(PoreSurfaceCalculation.process(), **inputs)
        self.report("pk: {} | Submitted pore_surface for structure {}".format(
            future.pid, inputs['structure']))

        return ToContext(**{label: Outputs(future)})

    # =========================================================================

    def run_distance_matrix(self):

        pore_surface_out = self.ctx.pore_surface

        label = "distance_matrix"
        inputs = {}
        inputs['_label'] = label
        inputs[
            '_description'] = "Computing the distance matrix for surface point cloud"
        inputs['code'] = self.inputs.distance_matrix_code
        inputs['surface_sample'] = pore_surface_out['surface_sample']
        inputs['cell'] = pore_surface_out['cell']
        inputs['_options'] = self.default_options

        self.out("pore_surface", pore_surface_out['surface_sample'])

        DistanceMatrixCalculation = CalculationFactory('phtools.dmatrix')
        future = submit(DistanceMatrixCalculation.process(), **inputs)
        self.report(
            "pk: {} | Submitted distance_matrix for structure {}".format(
                future.pid, self.inputs.structure.filename))

        return ToContext(**{label: Outputs(future)})

    # =========================================================================

    def run_rips_complex(self):
        distance_matrix_out = self.ctx.distance_matrix

        label = "rips_complex"
        inputs = {}
        inputs['_label'] = label
        inputs[
            '_description'] = "Computing the distance matrix for surface point cloud"
        inputs['code'] = self.inputs.rips_code
        #inputs['distance_matrix'] = distance_matrix_out['distance_matrix']
        inputs['remote_folder'] = distance_matrix_out['remote_folder']

        Parameters = DataFactory('gudhi.rdm')
        inputs['parameters'] = Parameters(dict={'max-edge-length': 4.2})
        inputs['_options'] = self.default_options

        RipsDistanceMatrixCalculation = CalculationFactory('gudhi.rdm')
        future = submit(RipsDistanceMatrixCalculation.process(), **inputs)
        self.report(
            "pk: {} | Submitted rips calculation for structure {}".format(
                future.pid, self.inputs.structure.filename))

        return ToContext(**{label: Outputs(future)})

    # =========================================================================

    def run_finish(self):
        self.out("barcode", self.ctx.rips_complex['rips_complex'])

        # Delete distance matrix again to save space
        # pylint: disable=protected-access
        self.ctx.distance_matrix['remote_folder']._clean()


@workfunction
def get_pore_surface_parameters(surface_area):
    """ Get input parameters for pore surface binary.

    Get input parameters for pore_surface binary from zeo++ output,
    while keeping data provenance.
    """
    PoreSurfaceParameters = DataFactory('phtools.surface')
    d = {
        'accessible_surface_area': surface_area.get_dict()['ASA_A^2'],
        'target_volume': 40e3,
        'sampling_method': 'random',
    }
    return PoreSurfaceParameters(dict=d)
