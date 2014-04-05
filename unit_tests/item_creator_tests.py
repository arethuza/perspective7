import unittest
import dbgateway
from item_creator import ItemCreator

import init_loader
from processor import Processor

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)

class ItemCreatorTests(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)
        pass

    @classmethod
    def tearDownClass(self):
        dbgw.reset()


if __name__ == '__main__':
    unittest.main()
