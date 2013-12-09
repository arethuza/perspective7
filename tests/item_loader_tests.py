import unittest
import dbgateway
import item_finder
import item_loader

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)

class Floop:
    pass

class ItemLoaderTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()

    def tearDown(self):
        self.setUp()

    def test_get_class(self):
        cls = item_loader.get_class("item_loader_tests.Floop")
        instance = cls()
        self.assertIsInstance(instance, Floop)

    def test_load_item(self):
        item_id = dbgw.create_item_initial(1, "test item", None, "{\"a\":1, \"b\":[1,2,3], \"c\":{\"raz\":\"alpha\"}}", "")
        type_id = dbgw.create_item_initial(1, "test type", None, "{ \"item_class\": \"item_loader_tests.Floop\" }", "")
        user_id = dbgw.create_item_initial(1, "test user", None, "{}", "")
        dbgw.set_item_type_user(item_id, type_id, "1", user_id)
        finder = item_finder.ItemFinder(LOCATOR)
        handle = finder.find("/test item")
        loader = item_loader.ItemLoader(LOCATOR)
        item = loader.load(handle)
        self.assertIsInstance(item, Floop)
        self.assertEquals(item.a, 1)
        self.assertEquals(len(item.b), 3)
        self.assertEquals(item.c["raz"], "alpha")
        self.assertFalse(isinstance(item.c, Floop))

    def test_get_classes(self):
        self.assertIsNotNone(item_loader.get_class("items.item.Item"))
        self.assertIsNotNone(item_loader.get_class("items.account_item.AccountItem"))

if __name__ == '__main__':
    unittest.main()
