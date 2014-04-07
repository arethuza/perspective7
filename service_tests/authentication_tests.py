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
                      failure_message="Request must contain Authorization header or parameter")
        common.log_in(self, "/", password=None, failure_status=403,
                      failure_message="Request must contain Authorization header or parameter")

    def test_access_with_token(self):
        common.log_in(self, "/")
        response = common.get_json(self, "/")
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)

    def test_access_with_bad_token(self):
        common.log_in(self, "/")
        working_auth_token = common.auth_token
        common.auth_token = common.auth_token[:-1]
        common.get_json(self, "/", failure_status=403, failure_message="Invalid authentication token")
        common.auth_token = "bearer "
        common.get_json(self, "/", failure_status=403, failure_message="Invalid authentication token")
        common.auth_token = " "
        common.get_json(self, "/", failure_status=403,
                        failure_message="Invalid format for Authorization header")
        common.auth_token = ""
        common.get_json(self, "/", failure_status=403,
                        failure_message="Invalid format for Authorization header")
        common.auth_token = working_auth_token
        response = common.get_json(self, "/")
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)

    def test_access_with_no_token(self):
        common.log_in(self, "/")
        common.get_json(self, "/", send_auth_header=False, failure_status=403,
                        failure_message="Request must contain Authorization header or parameter")

    def test_get_(self):
        common.log_in(self, "/")
        for i in range(1000):
            common.get_json(self, "/")


if __name__ == '__main__':
    unittest.main()
