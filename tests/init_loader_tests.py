import unittest
import dbgateway
import init_loader
import os

class InitLoaderTests(unittest.TestCase):

    LOCATOR="pq://postgres:password@localhost/perspective"

    def setUp(self):
        dbgw = dbgateway.DbGateway(self.LOCATOR)
        dbgw.delete_all()

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

if __name__ == '__main__':
    unittest.main()