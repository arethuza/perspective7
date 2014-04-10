import unittest
import dbgateway

import init_loader
from processor import Processor

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()
processor = Processor()

class UserItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")
        init_loader.load_init_data("data/user_item_tests.json")

    def tearDown(self):
        dbgw.reset()

    def test_post_set_password(self):
        user_item_handle = processor.item_finder.find("/users/test_user")
        user_item = processor.item_loader.load(user_item_handle)
        self.assertFalse(user_item.password_hash)
        processor.execute("/users/test_user", "post", "/users/test_user", {"password": "floop"})
        user_item = processor.item_loader.load(user_item_handle)
        self.assertTrue(user_item.password_hash)
        self.assertTrue(user_item.password_hash.startswith("bcrypt"))


if __name__ == '__main__':
    unittest.main()
