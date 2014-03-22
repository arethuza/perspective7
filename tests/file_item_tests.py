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

    def test_put_file_multiple_versions(self):
        # Put data to create a file - creates a new FileItem at /floop
        response = processor.execute("/floop", "put", "/users/system", {"_file_data": b'00000'})
        self.assertEquals(3, len(response))
        self.assertEquals(1, response["file_version"])
        self.assertEquals(5, response["length"])
        self.assertEquals("a5d50ea407a6c70cb8a4079415d01df8d67bfb2a", response["hash"])
        item_handle = processor.item_finder.find("/floop")
        self.assertEquals(1, item_handle.version)
        file_item = processor.item_loader.load(item_handle)
        self.assertEquals(1, file_item.file_version)
        file_data = processor.execute("/floop", "get", "/users/system", {})
        # Put data again to the same path, creating another version of the same file
        response = processor.execute("/floop", "put", "/users/system", {"_file_data": b'11111111111'})
        self.assertEquals(3, len(response))
        self.assertEquals(2, response["file_version"])
        self.assertEquals(11, response["length"])
        self.assertEquals("512504e13c3bb863c846ee0606037db973c27c1d", response["hash"])
        item_handle = processor.item_finder.find("/floop")
        self.assertEquals(2, item_handle.version)
        file_item = processor.item_loader.load(item_handle)
        self.assertEquals(2, file_item.file_version)

    def test_get_file_versions(self):
        processor.execute("/floop", "put", "/users/system", {"_file_data": b'0'})
        processor.execute("/floop", "put", "/users/system", {"_file_data": b'00'})
        processor.execute("/floop", "put", "/users/system", {"_file_data": b'000'})
        processor.execute("/floop", "put", "/users/system", {"_file_data": b'0000'})
        response = processor.execute("/floop", "get", "/users/system", {"versions": "true"})
        self.assertEquals(5, len(response))

    def test_put_file_and_get(self):
        # Create version 1
        processor.execute("/floop", "put", "/users/system", {"_file_data": b'01234'})
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {})
        self.assertEquals("floop", file_name)
        self.assertEquals(5, file_length)
        self.assertTrue(callable(block_yielder))
        block_count = 0
        for block_data in block_yielder():
            self.assertEquals(block_data, b'01234')
            block_count += 1
        self.assertEquals(block_count, 1)
        # Create version 2
        processor.execute("/floop", "put", "/users/system", {"_file_data": b'0123456789'})
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {})
        self.assertEquals("floop", file_name)
        self.assertEquals(10, file_length)
        self.assertTrue(callable(block_yielder))
        block_count = 0
        for block_data in block_yielder():
            self.assertEquals(block_data, b'0123456789')
            block_count += 1
        self.assertEquals(block_count, 1)
        # Get version 1
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {"file_version": "1"})
        self.assertEquals("floop", file_name)
        self.assertEquals(5, file_length)
        self.assertTrue(callable(block_yielder))
        block_count = 0
        for block_data in block_yielder():
            self.assertEquals(block_data, b'01234')
            block_count += 1
        self.assertEquals(block_count, 1)

    def test_post_file_put_blocks(self):
        # Create a file item by a POST
        result = processor.execute("/", "post", "/users/system", {"name": "floop", "type": "file"})
        self.assertEquals(result["file_version"], 0)
        # Write blocks of data
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0, "block_number": 0, "_file_data": b'0000000000000000000000'})
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0, "block_number": 1, "_file_data": b'11111111111111111111111111111'})
        with self.assertRaises(Exception) as cm:
            _, _, _ = processor.execute("/floop", "get", "/users/system", {"file_version": "0"})
        self.assertEquals("Bad file_version: 0", cm.exception.message)
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0, "block_number": 2, "_file_data": b'222222222222', "last_block": "true"})
        # Get the entire file contents
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {"file_version": "0"})
        self.assertEquals("floop", file_name)
        self.assertEquals(63, file_length)
        self.assertTrue(callable(block_yielder))
        # How many versions?
        response = processor.execute("/floop", "get", "/users/system", {"versions": "true"})
        self.assertEquals(1, len(response))


if __name__ == '__main__':
    unittest.main()
