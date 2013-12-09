import unittest
import dbgateway

import init_loader
from processor import Processor

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)

class ProcessorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)
        init_loader.load_init_data("data/finder_tests.json", LOCATOR)
        pass

    @classmethod
    def tearDownClass(self):
        dbgw.reset()

    def test_load_root_account(self):
        processor = Processor(LOCATOR)
        processor.execute("/", "get", "/", {})

if __name__ == '__main__':
    unittest.main()
