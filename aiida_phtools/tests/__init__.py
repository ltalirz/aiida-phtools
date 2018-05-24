""" Helper functions and classes for tests
"""
import os
import aiida.utils.fixtures
import unittest

TEST_DIR = os.path.dirname(os.path.realpath(__file__))

binaries = ['pore_surface', 'distance_matrix']


def get_backend():
    from aiida.backends.profile import BACKEND_DJANGO, BACKEND_SQLA
    if os.environ.get('TEST_AIIDA_BACKEND') == BACKEND_SQLA:
        return BACKEND_SQLA
    return BACKEND_DJANGO


def get_path_to_binary(binary):
    import distutils.spawn
    path = distutils.spawn.find_executable(binary)
    if path is None:
        raise ValueError("{} binary not found in PATH.")

    return path


def get_localhost_computer():
    """Setup localhost computer"""
    from aiida.orm import Computer
    import tempfile
    computer = Computer(
        name='localhost',
        description='my computer',
        hostname='localhost',
        workdir=tempfile.mkdtemp(),
        transport_type='local',
        scheduler_type='direct',
        enabled_state=True)

    return computer


def get_code(binary, plugin):
    """Setup code on localhost computer"""
    from aiida.orm import Code

    code = Code(
        files=[get_path_to_binary(binary)],
        input_plugin_name=plugin,
        local_executable=binary)
    code.label = binary

    return code


def get_temp_folder():
    """Returns AiiDA folder object.
    
    Useful for calculation.submit_test()
    """
    from aiida.common.folders import Folder
    import tempfile

    return Folder(tempfile.mkdtemp())


fixture_manager = aiida.utils.fixtures.FixtureManager()
fixture_manager.backend = get_backend()


class PluginTestCase(unittest.TestCase):
    """
    Set up a complete temporary AiiDA environment for plugin tests

    Filesystem:

        * temporary config (``.aiida``) folder
        * temporary repository folder

    Database:

        * temporary database cluster via the ``pgtest`` package
        * with aiida database user
        * with aiida_db database

    AiiDA:

        * set to use the temporary config folder
        * create and configure a profile
    """

    @classmethod
    def setUpClass(cls):
        from aiida.utils.capturing import Capturing
        cls.fixture_manager = fixture_manager
        if not fixture_manager.has_profile_open():
            with Capturing():
                cls.fixture_manager.create_profile()

    def tearDown(self):
        self.fixture_manager.reset_db()

    #@classmethod
    #def tearDownClass(cls):
    #    cls.fixture_manager.destroy_all()
