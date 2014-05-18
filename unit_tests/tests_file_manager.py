import unittest
import dbgateway
from file_manager import FileManager
from item_finder import ItemFinder
import init_loader
from worker import ServiceException

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()

class FileManagerTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")

    def tearDown(self):
        dbgw.reset()

    def test_create_file_versions(self):
        file_manager = FileManager()
        finder = ItemFinder()
        handle = finder.find("/")
        user_handle = finder.find("/users/system")
        file_version = file_manager.create_file_version(handle.item_id, None, user_handle)
        self.assertEquals(file_version, 0)
        file_version = file_manager.create_file_version(handle.item_id, None, user_handle)
        self.assertEquals(file_version, 1)
        file_version = file_manager.create_file_version(handle.item_id, 0, user_handle)
        self.assertEquals(file_version, 2)
        with self.assertRaises(ServiceException) as cm:
            file_version = file_manager.create_file_version(handle.item_id, 4, user_handle)
        self.assertEqual(cm.exception.response_code, 409)
        self.assertEqual("Unknown previous version: 4", cm.exception.message)

    def test_write_file_data(self):
        file_manager = FileManager()
        finder = ItemFinder()
        handle = finder.find("/")
        user_handle = finder.find("/users/system")
        file_version, file_length, file_hash = file_manager.write_file_data(handle.item_id, None, b'0000000000', user_handle)
        self.assertEquals(0, file_version)
        self.assertEquals(10, file_length)
        self.assertEquals("84d9c4b849506b6d8f8075a9000e7e0a254be71060ea889fad3c88395988f4fc", file_hash)

    def test_write_file_data_large(self):
        file_manager = FileManager()
        finder = ItemFinder()
        handle = finder.find("/")
        user_handle = finder.find("/users/system")
        data = b'0' * 13000000
        file_version, file_length, file_hash = file_manager.write_file_data(handle.item_id, None, data, user_handle)
        self.assertEquals(0, file_version)
        self.assertEquals(13000000, file_length)
        self.assertEquals("6ecd7e962d52419a6c649393b54b41ad95c2f700161b3f2470d7d16cc0aa101e", file_hash)

if __name__ == '__main__':
    unittest.main()
