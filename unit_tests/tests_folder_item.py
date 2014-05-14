import unittest
import dbgateway

import init_loader
from processor import Processor
from items.user_item import UserItem

from worker import ServiceException

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()
processor = Processor()

class FolderItemTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")

    def tearDown(self):
        dbgw.reset()

    def test_get(self):
        response = processor.execute("/system/types", "get", "/users/system", {})
        pass

if __name__ == '__main__':
    unittest.main()
