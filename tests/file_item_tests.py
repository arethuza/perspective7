import unittest
import dbgateway

import init_loader
from processor import Processor
from items.file_item import FileItem

from worker import ServiceException

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)
processor = Processor(LOCATOR)

class FileItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_create_file(self):
        processor.execute("/", "post", "/users/system", {"name": "test_user", "password": "floop"})
        response = processor.execute("/", "post", "/users/system", {"name": "new_file", "type": "file"})
        item_handle = processor.item_finder.find("/new_file")
        self.assertTrue(item_handle.can_read())
        item = processor.item_loader.load(item_handle)
        self.assertEquals(item.name, "new_file")
        self.assertTrue(isinstance(item, FileItem))

if __name__ == '__main__':
    unittest.main()
