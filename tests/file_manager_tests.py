import unittest
import dbgateway
from file_manager import FileManager
from item_finder import ItemFinder
import init_loader
from worker import ServiceException

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)

class FileManagerTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_create_file_version(self):
        file_manager = FileManager(LOCATOR)
        finder = ItemFinder(LOCATOR)
        handle = finder.find("/")
        user_handle = finder.find("/users/system")
        _, file_version = file_manager.create_file_version(handle.item_id, None, user_handle)
        self.assertEquals(file_version, 0)
        _, file_version = file_manager.create_file_version(handle.item_id, None, user_handle)
        self.assertEquals(file_version, 1)
        _, file_version = file_manager.create_file_version(handle.item_id, 0, user_handle)
        self.assertEquals(file_version, 2)
        with self.assertRaises(ServiceException) as cm:
            _, file_version = file_manager.create_file_version(handle.item_id, 4, user_handle)
        self.assertEqual(cm.exception.response_code, 409)
        self.assertEqual("Unknown previous version: 4", cm.exception.message)

if __name__ == '__main__':
    unittest.main()
