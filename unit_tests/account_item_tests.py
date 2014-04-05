import unittest
import dbgateway

import init_loader
from processor import Processor
from worker import ServiceException

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)
processor = Processor(LOCATOR)

class AccountItemTests(unittest.TestCase):

    def setUp(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)

    def tearDown(self):
        dbgw.reset()

    def test_create_user_and_login(self):
        processor.execute("/", "post", "/users/system", {"new_name": "test_user", "new_password": "floop"})
        response = processor.execute("/", "post", "/users/system",
                                                    {"name": "test_user", "password": "floop"})
        self.assertEqual(50, len(response["token"]))
        self.assertTrue(response["expires_at"])

    def test_login_unknown_user(self):
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "post", "/users/system", {"name": "unknown", "password": "floop"})
        self.assertEqual(cm.exception.response_code, 404)
        self.assertEqual(cm.exception.message, "Unknown user:unknown")

    def test_login_incorrect_password(self):
        processor.execute("/", "post", "/users/system", {"new_name": "test_user", "new_password": "floop"})
        with self.assertRaises(ServiceException) as cm:
            processor.execute("/", "post", "/users/system", {"name": "test_user", "password": "flop"})
        self.assertEqual(cm.exception.response_code, 403)
        self.assertEqual(cm.exception.message, "Bad password")

if __name__ == '__main__':
    unittest.main()
