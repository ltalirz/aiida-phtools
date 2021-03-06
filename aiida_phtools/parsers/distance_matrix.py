"""
Parsers provided by the plugin

Register parsers via the "aiida.parsers" entry point in setup.json.
"""
from aiida.parsers.parser import Parser
from aiida.parsers.exceptions import OutputParsingError

from aiida.orm import CalculationFactory
DistanceMatrixCalculation = CalculationFactory('phtools.dmatrix')


class DistanceMatrixParser(Parser):
    """
    Parser class for parsing output of multiplication.
    """

    def __init__(self, calculation):
        """
        Initialize Parser instance
        """
        super(DistanceMatrixParser, self).__init__(calculation)

        # check for valid input
        if not isinstance(calculation, DistanceMatrixCalculation):
            raise OutputParsingError(
                "Can only parse DistanceMatrixCalculation")

    # pylint: disable=protected-access
    def parse_with_retrieved(self, retrieved):
        """
        Parse output data folder, store results in database.

        :param retrieved: a dictionary of retrieved nodes, where
          the key is the link name
        :returns: a tuple with two values ``(bool, node_list)``, 
          where:

          * ``bool``: variable to tell if the parsing succeeded
          * ``node_list``: list of new nodes to be stored in the db
            (as a list of tuples ``(link_name, node)``)
        """
        success = False
        node_list = []

        # Check that the retrieved folder is there
        try:
            out_folder = retrieved['retrieved']
        except KeyError:
            self.logger.error("No retrieved folder found")
            return success, node_list

        # Check the folder content is as expected
        list_of_files = out_folder.get_folder_list()
        output_files = [self._calc._OUTPUT_FILE_NAME]
        # Note: set(A) <= set(B) checks whether A is a subset
        if set(output_files) <= set(list_of_files):
            pass
        else:
            self.logger.error(
                "Not all expected output files {} were found".format(
                    output_files))
            return success, node_list

        # Do not return distance matrix, as it is too large
        #from aiida.orm.data.singlefile import SinglefileData
        #node = SinglefileData(
        #    file=out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME))
        #node_list.append(('distance_matrix', node))

        success = True
        return success, node_list
