import fnmatch
import imp
import os
import sys
import unittest

ARMADA_BACKEND_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../armada_backend')
sys.path.append(ARMADA_BACKEND_PATH)

ARMADA_COMMAND_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../armada_command')
sys.path.append(ARMADA_COMMAND_PATH)


def _import_all_python_files_in_path(path):
    for root, dir_names, file_names in os.walk(path):
        for file_name in fnmatch.filter(file_names, '*.py'):
            file_path = os.path.join(root, file_name)
            imp.load_source('whatever', file_path)


class UnitTests(unittest.TestCase):
    def test_import_of_all_backend_python_files(self):
        _import_all_python_files_in_path(ARMADA_BACKEND_PATH)

    def test_import_of_all_command_python_files(self):
        _import_all_python_files_in_path(ARMADA_COMMAND_PATH)


if __name__ == '__main__':
    unittest.main()
