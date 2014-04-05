import unittest
from service_tests import service_tests_common as common

class AuthenticationTests(unittest.TestCase):

    def test_system_login(self):
        common.log_in(self, "/")
        common.log_in(self, "/", password="foo", failure_status=403, failure_message="Bad password")
        common.log_in(self, "/", password="", failure_status=403, failure_message="Bad password")
        common.log_in(self, "/", user="bar", failure_status=404, failure_message="Unknown user:bar")

if __name__ == '__main__':
    unittest.main()
