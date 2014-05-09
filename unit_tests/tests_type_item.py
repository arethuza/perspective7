import unittest
import dbgateway

import init_loader
from processor import Processor
from items.user_item import UserItem

from worker import ServiceException

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()
processor = Processor()


class TypeItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")

    def tearDown(self):
        dbgw.reset()

    def test_list_actions(self):
        response, _ = processor.execute("/system/types/item", "get", "/users/system", {})
        self.assertEquals(9, len(response))

if __name__ == '__main__':
    unittest.main()
