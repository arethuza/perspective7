import unittest
import dbgateway
import item_finder
import item_loader
import init_loader
import json

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()
finder = item_finder.ItemFinder()

class Floop:
    pass

class ItemLoaderTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()

    def tearDown(self):
        self.setUp()

    def test_load_item(self):
        item_id = dbgw.create_item_initial(1, "test item", None,
                                           json.dumps({
                                               "created_by_path": "/",
                                               "saved_by_path": "/",
                                               "props": {
                                                   "a": 1,
                                                   "b": [1,2,3],
                                                   "c": {"raz": "alpha"}}
                                           }), "")
        type_id = dbgw.create_item_initial(1, "test type", None,
                                           "{\"props\":{\"item_class\": \"tests_item_loader.Floop\" }}", "")
        user_id = dbgw.create_item_initial(1, "test user", None, "{}", "")
        dbgw.set_item_type_user(item_id, type_id, "1", user_id)
        finder = item_finder.ItemFinder()
        handle = finder.find("/test item")
        loader = item_loader.ItemLoader()
        item = loader.load(handle)
        self.assertIsInstance(item, Floop)
        self.assertEquals(item.props["a"], 1)
        self.assertEquals(len(item.props["b"]), 3)
        self.assertEquals(item.props["c"]["raz"], "alpha")
        self.assertFalse(isinstance(item.props["c"], Floop))

    def test_load_item_type(self):
        init_loader.load_init_data("../database/init.json")
        loader = item_loader.ItemLoader()
        type_item = loader.load_type("item")
        self.assertEqual("/system/types/item", type_item.handle.path)
        self.assertIsNotNone(type_item)
        self.assertEqual(str(type_item.handle.item_id), type_item.type_path)
        # Some intermediate ids are cached in loader, so do this twice
        type_item = loader.load_type("item")
        self.assertIsNotNone(type_item)
        self.assertEqual(str(type_item.handle.item_id), type_item.type_path)
        self.assertEqual("/system/types/item", type_item.handle.path)

    def test_load_template_json(self):
        init_loader.load_init_data("../database/init.json")
        loader = item_loader.ItemLoader()
        data = json.loads(loader.load_template_json("not a type name"))
        self.assertEqual(data["title"], "New Item")
        data = json.loads(loader.load_template_json("item"))
        self.assertEqual(data["title"], "New Item")

if __name__ == '__main__':
    unittest.main()
