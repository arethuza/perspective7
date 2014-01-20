import unittest
import dbgateway

import init_loader
from processor import Processor
from items.user_item import UserItem

from worker import ServiceException

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)
processor = Processor(LOCATOR)

class ItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_create_item_default_type(self):
        processor.execute("/", "post", "/users/system", {"name": "test_user", "password": "floop"})
        response = processor.execute("/", "post", "/users/system", {"name": "new_item"})
        item_handle = processor.item_finder.find("/new_item")
        self.assertTrue(item_handle.can_read())
        item = processor.item_loader.load(item_handle)
        self.assertEquals(item.name, "new_item")

    def test_create_item_with_type(self):
        processor.execute("/", "post", "/users/system", {"name": "test_user", "password": "floop"})
        response = processor.execute("/", "post", "/users/system", {"name": "new_item", "type": "user"})
        item_handle = processor.item_finder.find("/new_item")
        self.assertTrue(item_handle.can_read())
        item = processor.item_loader.load(item_handle)
        self.assertEquals(item.name, "new_item")
        self.assertTrue(isinstance(item, UserItem))

    def test_create_item_bad_type(self):
        processor.execute("/", "post", "/users/system", {"name": "test_user", "password": "floop"})
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "post", "/users/system", {"name": "new_item", "type": "floop"})
        self.assertEqual(cm.exception.response_code, 403)
        self.assertEqual(cm.exception.message, "Unknown item type:floop")

if __name__ == '__main__':
    unittest.main()
