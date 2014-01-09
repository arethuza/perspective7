import unittest
import dbgateway

import init_loader
from processor import Processor

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)
processor = Processor(LOCATOR)

class AccountItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_post_set_password(self):
        user_handle = processor.item_finder.find("/users/test_user")
        self.assertEqual(user_handle.get_auth_name(), "none")
        processor.execute("/", "post", "/users/system", {"name": "test_user", "password": "floop"})
        user_handle = processor.item_finder.find("/users/test_user")
        self.assertEqual(user_handle.get_auth_name(), "reader")
        user_item = processor.item_loader.load(user_handle)
        self.assertTrue(user_item.password_hash.startswith("bcrypt"))


if __name__ == '__main__':
    unittest.main()
