import unittest
import dbgateway
import init_loader
import item_finder

LOCATOR="pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)

class ItemFinderTestsInitData(unittest.TestCase):

    finder = item_finder.ItemFinder(LOCATOR)

    @classmethod
    def setUpClass(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)
        init_loader.load_init_data("data/finder_tests.json", LOCATOR)
        pass

    @classmethod
    def tearDownClass(self):
        dbgw.reset()

    def test_find_root_anon(self):
        handle = self.finder.find("/")
        self.assertEquals(handle.path, "/")
        self.assertEquals(handle.item_id, 1)
        self.assertEquals(handle.auth_level, item_finder.AuthLevels["reader"])
        self.assertIsNone(handle.user_handle)

    def test_find_system_user(self):
        system_user_handle = self.finder.find_system_user()
        self.assertEquals(system_user_handle.path, "/users/system")
        self.assertTrue(system_user_handle.item_id > 1)
        self.assertEquals(system_user_handle.auth_level, item_finder.AuthLevels["reader"])
        self.assertIsNone(system_user_handle.user_handle)

    def test_system_user_auth(self):
        system_user_handle = self.finder.find_system_user()
        paths = ["/users", "/system", "/system/types/type"]
        found_ids = set()
        for path in paths:
            handle = self.finder.find(path, system_user_handle)
            self.assertEquals(handle.path, path)
            self.assertTrue(handle.item_id > 1)
            self.assertTrue(handle.item_id not in found_ids)
            self.assertEquals(handle.auth_level, item_finder.AuthLevels["system"])
            self.assertEquals(handle.user_handle, system_user_handle)
            found_ids.add(handle.item_id)

    def test_bob_read_paris_private(self):
        bob_handle = self.finder.find("/paris/bob")
        private_handle = self.finder.find("/paris/private", bob_handle)
        self.assertEquals(private_handle.auth_level, item_finder.AuthLevels["editor"])

    def test_bob_fail_milan_private(self):
        bob_handle = self.finder.find("/paris/bob")
        private_handle = self.finder.find("/milan/private", bob_handle)
        self.assertEquals(private_handle.auth_level, item_finder.AuthLevels["none"])

    def test_alice_read_milan_private(self):
        alice_handle = self.finder.find("/milan/alice")
        private_handle = self.finder.find("/milan/private", alice_handle)
        self.assertEquals(private_handle.auth_level, item_finder.AuthLevels["editor"])

    def test_bob_fail_milan_private(self):
        alice_handle = self.finder.find("/milan/alice")
        private_handle = self.finder.find("/paris/private", alice_handle)
        self.assertEquals(private_handle.auth_level, item_finder.AuthLevels["none"])

    def test_find_no_item(self):
        alice_handle = self.finder.find("/milan/alice")
        no_item_handle = self.finder.find("/not/there", alice_handle)
        self.assertIsNone(no_item_handle.item_id)
        self.assertEquals(no_item_handle.path, "/not/there")
        self.assertEquals(no_item_handle.user_handle.path, "/milan/alice")
        self.assertEquals(no_item_handle.auth_level, item_finder.AuthLevels["none"])
