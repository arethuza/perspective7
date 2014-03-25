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

    def test_create_file_versions(self):
        file_manager = FileManager(LOCATOR)
        finder = ItemFinder(LOCATOR)
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
        file_manager = FileManager(LOCATOR)
        finder = ItemFinder(LOCATOR)
        handle = finder.find("/")
        user_handle = finder.find("/users/system")
        response = file_manager.write_file_data(handle.item_id, None, b'0000000000', user_handle)
        self.assertEquals(0, response["file_version"])
        self.assertEquals(10, response["length"])
        self.assertEquals("ef49b18cac3f4b7dc5346763309f6ac6e763c575", response["hash"])

    def test_write_file_data_large(self):
        file_manager = FileManager(LOCATOR)
        finder = ItemFinder(LOCATOR)
        handle = finder.find("/")
        user_handle = finder.find("/users/system")
        data = b'0' * 13000000
        response = file_manager.write_file_data(handle.item_id, None, data, user_handle)
        self.assertEquals(0, response["file_version"])
        self.assertEquals(13000000, response["length"])
        self.assertEquals("621acfe4950f45e38ebfefaef03b1b0d69a854de", response["hash"])

if __name__ == '__main__':
    unittest.main()
