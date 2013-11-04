import unittest
import dbgateway

class DbGatewayTests(unittest.TestCase):

    LOCATOR="pq://postgres:password@localhost/perspective"

    def setUp(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.delete_all()

    def tearDown(self):
        self.setUp()

    def test_delete_all(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.delete_all()

    def test_create_item_bootstrap(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.create_item_bootstrap(None, "foo", "1.2", "{ \"raz\": 1 }", "raz")


if __name__ == '__main__':
    unittest.main()