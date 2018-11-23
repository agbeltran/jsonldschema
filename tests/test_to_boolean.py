import unittest
import utils


class ToBooleanTestCase(unittest.TestCase):

    def test_to_bolean(self):
        val = utils.to_boolean("yes")
        self.assertTrue(val is True)

        val2 = utils.to_boolean("no")
        self.assertTrue(val2 is False)

        val3 = utils.to_boolean("pouet")
        self.assertTrue(isinstance(val3, Exception))
