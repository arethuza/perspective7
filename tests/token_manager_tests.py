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
        token_value, expires_at = tm.create_token(handle.item_id, 50, days=10)
        self.assertEquals(len(token_value), 50)
        self.assertTrue(expires_at)
        self.assertTrue(tm.find_token(handle.item_id, token_value))

    def test_fail_find_expired(self):
        handle = finder.find("/")
        tm = token_manager.TokenManager(LOCATOR)
        # Create token that expires immediately
        token_value, expires_at = tm.create_token(handle.item_id, 50, seconds=0)
        self.assertEquals(len(token_value), 50)
        self.assertTrue(expires_at)
        time.sleep(1)
        self.assertFalse(tm.find_token(handle.item_id, token_value))


if __name__ == '__main__':
    unittest.main()
