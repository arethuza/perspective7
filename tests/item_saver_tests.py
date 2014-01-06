import unittest
import dbgateway
import item_finder
import item_loader
import init_loader
import item_saver
import json

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)
finder = item_finder.ItemFinder(LOCATOR)
loader = item_loader.ItemLoader(LOCATOR)
saver = item_saver.ItemSaver(LOCATOR)

class Floop:
    pass

class ItemSaverTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)
        init_loader.load_init_data("data/saver_tests.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_save_item_no_changes(self):
        user_handle = finder.find_system_user()
        item_handle = finder.find("/test")
        item = loader.load(item_handle)
        saver.save(item, user_handle)

    def test_save_item_changes(self):
        user_handle = finder.find_system_user()
        item_handle0 = finder.find("/test")
        self.assertEqual(item_handle0.version, 0)
        # Load, update and save to create version 1
        item = loader.load(item_handle0)
        item.set_field("floop", [1,2,3])
        saver.save(item, user_handle)
        # Load, update and save to create version 2
        item_handle1 = finder.find("/test")
        item = loader.load(item_handle1)
        self.assertEqual(item_handle1.version, 1)
        self.assertEqual(item.floop, [1, 2, 3])
        item.set_field("floop", "raz")
        saver.save(item, user_handle)
        # Check version 2
        item_handle2 = finder.find("/test")
        item = loader.load(item_handle2)
        self.assertEqual(item_handle2.version, 2)
        self.assertEqual(item.floop, "raz")

if __name__ == '__main__':
    unittest.main()
