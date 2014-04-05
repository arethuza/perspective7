import unittest
from service_tests import service_tests_common as common

class AuthenticationTests(unittest.TestCase):

    def test_system_login(self):
        common.log_in(self, "/")

if __name__ == '__main__':
    unittest.main()
