""" Tests for the workflows

"""
import os
import aiida_phtools.tests as pt
import aiida_zeopp.tests as zt


class TestDistanceMatrixWorkChain(pt.PluginTestCase):
    def setUp(self):

        # set up test computer
        self.computer = pt.get_localhost_computer().store()
        self.zeopp_code = zt.get_network_code(self.computer).store()
        self.pore_surface_code = pt.get_code(
            plugin='phtools.surface', computer=self.computer).store()
        self.distance_matrix_code = pt.get_code(
            plugin='phtools.dmatrix', computer=self.computer).store()

    def test_run_workchain(self):
        """Test running the WorkChain"""
        from aiida.work.run import run
        from aiida.orm.data.cif import CifData
        from aiida_zeopp.tests import TEST_DIR
        from aiida_phtools.workflows.dmatrix import DistanceMatrixWorkChain

        structure = CifData(
            file=os.path.join(TEST_DIR, 'HKUST-1.cif'), parse_policy='lazy')

        outputs = run(
            DistanceMatrixWorkChain,
            structure=structure,
            zeopp_code=self.zeopp_code,
            pore_surface_code=self.pore_surface_code,
            distance_matrix_code=self.distance_matrix_code,
        )

        print(outputs)
