import unittest
from service_tests import service_tests_common as common

class AuthenticationTests(unittest.TestCase):

    def test_system_login(self):
        # Login OK
        common.log_in(self, "/")
        # bad name and/or password
        common.log_in(self, "/", password="foo", failure_status=403, failure_message="Bad password")
        common.log_in(self, "/", password="", failure_status=403, failure_message="Bad password")
        common.log_in(self, "/", name="bar", failure_status=404, failure_message="Unknown user:bar")
        common.log_in(self, "/", name="bar", password="floop", failure_status=404, failure_message="Unknown user:bar")
        # Missing password or name
        common.log_in(self, "/", name=None, failure_status=403,
                      failure_message="Request must contain Authorization header or as parameter")
        common.log_in(self, "/", password=None, failure_status=403,
                      failure_message="Request must contain Authorization header or as parameter")

if __name__ == '__main__':
    unittest.main()
