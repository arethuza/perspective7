import unittest
import dbgateway
from item_creator import ItemCreator

import init_loader
from processor import Processor

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()
processor = Processor()

class ItemCreatorTests(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")
        pass

    @classmethod
    def tearDownClass(self):
        dbgw.reset()


if __name__ == '__main__':
    unittest.main()
