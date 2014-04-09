import unittest
import dbgateway
from worker import Worker

import init_loader
from processor import Processor
from worker import Worker

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgateway.set_for_thread(LOCATOR)
dbgw = dbgateway.get_from_thread()

class WorkerTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_create(self):
        processor = Processor(LOCATOR)
        worker = processor.get_worker("/", "/users/system")
        handle = worker.create("floop", "folder")
        self.assertEqual("/floop", handle.path)

    def test_find_or_create(self):
        processor = Processor(LOCATOR)
        worker = processor.get_worker("/", "/users/system")
        self.assertIsNone(worker.find("floop").item_id)
        handle1 = worker.find_or_create("floop", "folder")
        handle2 = worker.find_or_create("floop", "folder")
        self.assertEqual("/floop", handle1.path)
        self.assertEqual("/floop", handle2.path)
        self.assertTrue(handle1.item_id == handle2.item_id)

    def test_move(self):
        processor = Processor(LOCATOR)
        worker = processor.get_worker("/", "/users/system")
        worker.move("users")
        self.assertEqual("/users", worker.current_item.handle.path)
        worker.move("system")
        self.assertEqual("/users/system", worker.current_item.handle.path)
        self.assertRaises(Exception, worker.move, "not there")

if __name__ == '__main__':
    unittest.main()
