import unittest
import dbgateway
import token_manager
import item_finder
import init_loader
import datetime
import time

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)
finder = item_finder.ItemFinder(LOCATOR)

class TokenManagerTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_create_find_token(self):
        handle = finder.find("/")
        tm = token_manager.TokenManager(LOCATOR)
        token_value, expires_at = tm.create_token(handle.item_id, 50, {"path": "/foo"}, days=10)
        self.assertEquals(len(token_value), 50)
        self.assertTrue(expires_at)
        item_id, data = tm.find_token(token_value)
        self.assertEquals(handle.item_id, item_id)
        self.assertEquals(data, {"path": "/foo"})

    def test_fail_find_expired(self):
        handle = finder.find("/")
        tm = token_manager.TokenManager(LOCATOR)
        # Create token that expires immediately
        token_value, expires_at = tm.create_token(handle.item_id, 50, {"path": "/foo"}, seconds=0)
        self.assertEquals(len(token_value), 50)
        self.assertTrue(expires_at)
        time.sleep(1)
        item_id, data = tm.find_token(token_value)
        self.assertIsNone(item_id)
        self.assertIsNone(data)


if __name__ == '__main__':
    unittest.main()
