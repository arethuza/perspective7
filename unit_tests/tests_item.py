import unittest
import dbgateway

import init_loader
from processor import Processor
from items.user_item import UserItem

from worker import ServiceException

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()
processor = Processor()

class ItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")

    def tearDown(self):
        dbgw.reset()

    def test_create_item_default_type(self):
        response = processor.execute("/", "post", "/users/system", {"name": "new_item"})
        item_handle = processor.item_finder.find("/new_item")
        self.assertTrue(item_handle.can_read())
        item = processor.item_loader.load(item_handle)
        self.assertEquals(item.name, "new_item")

    def test_create_item_with_type(self):
        response = processor.execute("/", "post", "/users/system", {"name": "new_item", "type": "user"})
        item_handle = processor.item_finder.find("/new_item")
        self.assertTrue(item_handle.can_read())
        item = processor.item_loader.load(item_handle)
        self.assertEquals(item.name, "new_item")
        self.assertTrue(isinstance(item, UserItem))

    def test_create_item_bad_type(self):
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "post", "/users/system", {"name": "new_item", "type": "floop"})
        self.assertEqual(cm.exception.response_code, 403)
        self.assertEqual(cm.exception.message, "Unknown item type:floop")

    def test_delete_item(self):
        processor.execute("/", "post", "/users/system", {"name": "foo"})
        self.assertIsNotNone(processor.execute("/foo", "get", "/users/system", {}))
        processor.execute("/foo", "post", "/users/system", {"name": "bar"})
        self.assertIsNotNone(processor.execute("/foo/bar", "get", "/users/system", {}))
        processor.execute("/foo", "delete", "/users/system", {})
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/foo", "get", "/users/system", {})
        self.assertEqual(cm.exception.response_code, 404)
        self.assertEqual(cm.exception.message, "bad path:/foo")
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/foo/bar", "get", "/users/system", {})
        self.assertEqual(cm.exception.response_code, 404)
        self.assertEqual(cm.exception.message, "bad path:/foo/bar")

    def test_delete_item_not_deletable(self):
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "delete", "/users/system", {})
        self.assertEqual(cm.exception.response_code, 403)
        self.assertEqual(cm.exception.message, "Item cannot be deleted")

    def test_set_item_name(self):
        processor.execute("/", "post", "/users/system", {"name": "new_item", "type": "item"})
        item_handle = processor.item_finder.find("/new_item")
        self.assertTrue(item_handle.can_read())
        processor.execute("/new_item", "put", "/users/system", {"name": "new_name"})
        item_handle = processor.item_finder.find("/new_item")
        self.assertFalse(item_handle.can_read())
        item_handle = processor.item_finder.find("/new_name")
        self.assertTrue(item_handle.can_read())

    def test_create_user_and_login_through_item(self):
        processor.execute("/", "post", "/users/system", {"new_name": "test_user", "new_password": "floop"})
        processor.execute("/", "post", "/users/system", {"name": "test_item", "type": "item"})
        response = processor.execute("/test_item", "post", "/users/system",
                                                    {"name": "test_user", "password": "floop"})
        self.assertEqual(50, len(response["token"]))
        self.assertTrue(response["expires_at"])

    def test_create_item_twice(self):
        processor.execute("/", "post", "/users/system", {"name": "test_item", "type": "item"})
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "post", "/users/system", {"name": "test_item", "type": "item"})
        self.assertEqual(403, cm.exception.response_code, 403)
        self.assertEqual("Failed to create item: test_item", cm.exception.message)

    def test_bad_param_name(self):
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "post", "/users/system", {"name": "test_item", "typ": "item"})
        self.assertEqual(403, cm.exception.response_code, 403)
        self.assertEqual("No matching action", cm.exception.message)


if __name__ == '__main__':
    unittest.main()
