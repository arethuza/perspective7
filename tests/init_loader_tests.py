import unittest
import dbgateway
import init_loader
import os

class InitLoaderTests(unittest.TestCase):

    LOCATOR="pq://postgres:password@localhost/perspective"

    def setUp(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.reset()

    def tearDown(self):
        self.setUp()

    def test_load_json_with_comments(self):
        data = init_loader.load_json_with_comments("data/json_with_comments.json")
        self.assertEqual(data["foo"], 1)
        bar = data["bar"]
        self.assertTrue(type(bar) is list)
        self.assertEqual(len(bar), 3)
        self.assertEqual(bar[0], 3)
        self.assertEqual(bar[1], 4)
        self.assertEqual(bar[2], 5)

    def test_find_item_id(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.create_item_initial(None, "", "", "{}", "")
        item_id = dbgw.create_item_initial(1,       "foo", "1", "{}", "")
        item_id = dbgw.create_item_initial(item_id, "bar", "1.2", "{}", "")
        item_id = dbgw.create_item_initial(item_id, "raz", "1.2.3", "{}", "")
        found_id, found_id_path = init_loader.find_item_id(dbgw, "/foo/bar/raz")
        self.assertEquals(found_id, item_id)
        self.assertEquals(found_id_path, "1.2.3.4")

    def test_find_item_root(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.create_item_initial(None, "", "", "{}", "")
        found_id, found_id_path = init_loader.find_item_id(dbgw, "/")
        self.assertEquals(found_id, 1)
        self.assertEquals(found_id_path, "1")

    def test_load_init_data(self):
        init_loader.load_init_data("../database/init.json", self.LOCATOR)

if __name__ == '__main__':
    unittest.main()