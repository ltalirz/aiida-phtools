""" Tests for the workflows

"""
import os
import aiida_phtools.tests as pt
import aiida_zeopp.tests as zt
import aiida_gudhi.tests as gt


class TestDistanceMatrixWorkChain(pt.PluginTestCase):
    def setUp(self):

        # set up test computer
        self.zeopp_code = zt.get_code(entry_point='zeopp.network')
        self.pore_surface_code = pt.get_code(entry_point='phtools.surface')
        self.distance_matrix_code = pt.get_code(entry_point='phtools.dmatrix')
        self.rips_code = gt.get_code(entry_point='gudhi.rdm')

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
            rips_code=self.rips_code,
        )

        print(outputs)
