""" Example submission of work chain """
import os
from aiida_phtools.workflows.dmatrix import DistanceMatrixWorkChain
import aiida_phtools.tests as pt
import aiida_zeopp.tests as zt
import aiida_gudhi.tests as gt

from aiida.work.run import submit
from aiida.orm.data.cif import CifData
from aiida_zeopp.tests import TEST_DIR

structure = CifData(
    file=os.path.join(TEST_DIR, 'HKUST-1.cif'), parse_policy='lazy')

outputs = submit(
    DistanceMatrixWorkChain,
    structure=structure,
    zeopp_code=zt.get_code(entry_point='zeopp.network'),
    pore_surface_code=pt.get_code(entry_point='phtools.surface'),
    distance_matrix_code=pt.get_code(entry_point='phtools.dmatrix'),
    rips_code=gt.get_code(entry_point='gudhi.rdm'),
)
