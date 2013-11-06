import unittest
import dbgateway


class DbGatewayTests(unittest.TestCase):

    LOCATOR="pq://postgres:password@localhost/perspective"

    def setUp(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.reset()

    def tearDown(self):
        self.setUp()

    def test_delete_all(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.reset()

    def test_create_item_initial(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        item_id = dbgw.create_item_initial(None, "foo", "_", "{ \"raz\": 1 }", "raz")
        self.assertEquals(item_id, 1)

    def test_create_item_initial_and_find_id(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.create_item_initial(None, "", None, "{ \"raz\": 1 }", "raz")
        dbgw.create_item_initial(1, "foo", "1", "{ \"bar\": 1 }", "foo")
        item_id, item_id_path = dbgw.find_id(1, "foo")
        self.assertTrue(item_id > 1)
        self.assertEquals(item_id_path, "1.2")

if __name__ == '__main__':
    unittest.main()