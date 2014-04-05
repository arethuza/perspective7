import unittest
import dbgateway

import init_loader
from processor import Processor
from items.file_item import FileItem
from file_manager import BLOCK_LENGTH

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
        self.assertEquals(4, len(response))
        self.assertEquals(1, response["file_version"])
        self.assertEquals(1, response["file_version"])
        self.assertEquals(5, response["file_length"])
        self.assertEquals("a5d50ea407a6c70cb8a4079415d01df8d67bfb2a", response["file_hash"])
        item_handle = processor.item_finder.find("/floop")
        self.assertEquals(1, item_handle.version)
        file_item = processor.item_loader.load(item_handle)
        self.assertEquals(1, file_item.file_version)
        file_data = processor.execute("/floop", "get", "/users/system", {})
        # Put data again to the same path, creating another version of the same file
        response = processor.execute("/floop", "put", "/users/system", {"_file_data": b'11111111111'})
        self.assertEquals(4, len(response))
        self.assertEquals(2, response["file_version"])
        self.assertEquals(2, response["file_version"])
        self.assertEquals(11, response["file_length"])
        self.assertEquals("512504e13c3bb863c846ee0606037db973c27c1d", response["file_hash"])
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
        # Create file_version 1
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
        # Create file_version 2
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
        # Get file_version 1
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {"file_version": "2"})
        self.assertEquals("floop", file_name)
        self.assertEquals(10, file_length)
        self.assertTrue(callable(block_yielder))
        block_count = 0
        for block_data in block_yielder():
            self.assertEquals(block_data, b'0123456789')
            block_count += 1
        self.assertEquals(block_count, 1)

    def test_post_file_put_blocks(self):
        # Create a file item by a POST
        result = processor.execute("/", "post", "/users/system", {"name": "floop", "type": "file"})
        self.assertEquals(result["file_version"], 0)
        # Write blocks of data
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 0,
                           "_file_data": b'0'*BLOCK_LENGTH})
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 1,
                           "last_block": False,
                           "_file_data": b'1'*BLOCK_LENGTH})
        with self.assertRaises(Exception) as cm:
            _, _, _ = processor.execute("/floop", "get", "/users/system", {"file_version": "0"})
        self.assertEquals("Bad file_version: 0", cm.exception.message)
        last_block_data = b'222222222222'
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 2,
                           "last_block": "true",
                           "_file_data": last_block_data})
        # Get the entire file contents
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {"file_version": "0"})
        self.assertEquals("floop", file_name)
        self.assertEquals((2 * BLOCK_LENGTH) + len(last_block_data), file_length)
        self.assertTrue(callable(block_yielder))
        # How many versions?
        response = processor.execute("/floop", "get", "/users/system", {"versions": "true"})
        self.assertEquals(1, len(response))
        # Check the block data
        generator = block_yielder()
        block0 = next(generator)
        block1 = next(generator)
        block2 = next(generator)
        self.assertEquals(block0,  b'0'*BLOCK_LENGTH)
        self.assertEquals(block1,  b'1'*BLOCK_LENGTH)
        self.assertEquals(block2,  b'222222222222')

    def test_post_file_put_completed_repeat_fails(self):
        # Create a file item by a POST
        result = processor.execute("/", "post", "/users/system", {"name": "floop", "type": "file"})
        self.assertEquals(result["file_version"], 0)
        # Write blocks of data
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 0,
                           "last_block": True,
                           "_file_data": b'33333333333333333333'})
        # Write same block again
        with self.assertRaises(Exception) as cm:
            processor.execute("/floop", "put", "/users/system",
                              {"file_version": 0,
                               "block_number": 0,
                               "last_block": True,
                               "_file_data": b'33333333333333333333333'})
        self.assertEquals("File version is complete", cm.exception.message)

    def test_post_file_put_repeat(self):
        # Create a file item by a POST
        result = processor.execute("/", "post", "/users/system", {"name": "floop", "type": "file"})
        self.assertEquals(result["file_version"], 0)
        # Write blocks of data
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 0,
                           "last_block": False,
                           "_file_data": b'0' * BLOCK_LENGTH})
        # Write again to same block
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 0,
                           "last_block": False,
                           "_file_data": b'1' * BLOCK_LENGTH})
        # Complete the file
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 1,
                           "last_block": True,
                           "_file_data": b'33333333333333333333'})
        # Check the file
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system",
                                                                  {"file_version": "0"})
        self.assertEquals(file_length, BLOCK_LENGTH + 20)
        generator = block_yielder()
        block0 = next(generator)
        block1 = next(generator)
        self.assertEquals(block0,  b'1'*BLOCK_LENGTH)
        self.assertEquals(block1,  b'33333333333333333333')

    def test_post_put_versions_single_block_update(self):
        # Create a file item by a POST
        result = processor.execute("/", "post", "/users/system", {"name": "floop", "type": "file"})
        self.assertEquals(result["file_version"], 0)
        # Create file_version 0
        # Write blocks of data to version 0
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 0,
                           "last_block": False,
                           "_file_data": b'0' * BLOCK_LENGTH})
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 1,
                           "last_block": False,
                           "_file_data": b'1' * BLOCK_LENGTH})
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 0,
                           "block_number": 2,
                           "last_block": True,
                           "_file_data": b'2222222222222222222'})
        # Check the file
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {})
        generator = block_yielder()
        block0 = next(generator)
        block1 = next(generator)
        block2 = next(generator)
        self.assertEquals(block0,  b'0'*BLOCK_LENGTH)
        self.assertEquals(block1,  b'1'*BLOCK_LENGTH)
        self.assertEquals(block2,  b'2222222222222222222')
        # post to create a new version of the file item
        response = processor.execute("/floop", "post", "/users/system", {"previous": 0})
        self.assertEquals(1, response["file_version"])
        # Write a single block of data to version 1
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 1,
                           "block_number": 0,
                           "last_block": False,
                           "_file_data": b'3' * BLOCK_LENGTH})
        processor.execute("/floop", "put", "/users/system",
                          {"file_version": 1,
                           "block_number": 2,
                           "last_block": True,
                           "_file_data": b''})
        # Check the file - that we have replaced block 0 with [3] * BLOCK_LENGTH
        file_name, file_length, block_yielder = processor.execute("/floop", "get", "/users/system", {})
        generator = block_yielder()
        block0 = next(generator)
        block1 = next(generator)
        block2 = next(generator)
        # self.assertEquals(block0,  b'3'*BLOCK_LENGTH)
        self.assertEquals(block1,  b'1'*BLOCK_LENGTH)
        self.assertEquals(block2,  b'2222222222222222222')

if __name__ == '__main__':
    unittest.main()
