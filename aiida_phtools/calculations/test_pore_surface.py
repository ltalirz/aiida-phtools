""" Tests for calculations

"""
import os
import aiida_phtools.tests as pt


class TestPoreSurface(pt.PluginTestCase):
    def setUp(self):

        # set up test computer
        self.code = pt.get_code(entry_point='phtools.surface')

    def test_submit_HKUST1(self):
        """Test submitting a calculation"""
        from aiida_phtools.tests import TEST_DIR

        code = self.code

        # set up calculation
        calc = code.new_calc()
        calc.label = "aiida_phtools example calculation"
        calc.set_max_wallclock_seconds(1 * 60)
        calc.set_withmpi(False)
        calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})

        # Prepare input parameters
        from aiida.orm import DataFactory
        PoreSurfaceParameters = DataFactory('phtools.surface')
        d = {
            'accessible_surface_area': 4464.02,
            'target_volume': 40e3,
            'sampling_method': 'random',
        }
        parameters = PoreSurfaceParameters(dict=d)
        calc.use_parameters(parameters)

        SinglefileData = DataFactory('singlefile')
        structure = SinglefileData(file=os.path.join(TEST_DIR, 'HKUST-1.cssr'))
        calc.use_structure(structure)

        surface_sample = SinglefileData(
            file=os.path.join(TEST_DIR, 'HKUST-1.vsa'))
        calc.use_surface_sample(surface_sample)

        calc.store_all()
        #calc.submit()
        calc.submit_test(folder=pt.get_temp_folder())
