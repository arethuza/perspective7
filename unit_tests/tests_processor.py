import unittest
import dbgateway

import init_loader
from processor import Processor
from worker import ServiceException

dbgateway.locator = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.get()

class ProcessorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json")

    @classmethod
    def tearDownClass(self):
        dbgw.reset()

    def test_load_root_account(self):
        processor = Processor()
        processor.execute("/", "get", "/", {})

    def test_create_user_login(self):
        processor = Processor()
        # Create a user
        processor.execute("/", "post", "/users/system", {"new_name": "test_user", "new_password": "floop"})
        # Login as user
        response = processor.check_login("/", "post", {"name": "test_user", "password": "floop"})
        # Authenticate using token
        user_handle = processor.get_user_for_token(response["token"])
        # Get the user handle directly
        user_handle2 = processor.item_finder.find("/users/test_user")
        # They are handles for the same item
        self.assertTrue(user_handle.item_id == user_handle2.item_id)
        # An incorrect token can't be used
        with self.assertRaises(ServiceException) as cm:
            processor.get_user_for_token(response["token"] + "foo")
        self.assertEqual(cm.exception.response_code, 403)
        self.assertEqual(cm.exception.message, "Invalid authentication token")
        # An empty token can't be used
        with self.assertRaises(ServiceException) as cm:
            processor.get_user_for_token("")
        self.assertEqual(cm.exception.response_code, 403)
        self.assertEqual(cm.exception.message, "Invalid authentication token")
        # Check we can do something with the user handle we just retrieved - change the user's password
        processor.execute("/users/test_user", "post", user_handle, {"password": "raz"})

if __name__ == '__main__':
    unittest.main()
