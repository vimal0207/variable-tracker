import unittest
from variable_tracker import Setup


class TestSetupImport(unittest.TestCase):

    def test_import(self):
        self.assertIsInstance(Setup, type)
        # Further tests can be added based on the behavior of Setup


if __name__ == "__main__":
    unittest.main()
