import unittest
import dbgateway
import init_loader
import item_finder

LOCATOR="pq://postgres:password@localhost/perspective"
dbgateway.set_for_thread(LOCATOR)
dbgw = dbgateway.get_from_thread()

class ItemFinderTestsInitData(unittest.TestCase):

    finder = item_finder.ItemFinder(LOCATOR)

    @classmethod
    def setUpClass(cls):
        dbgw.reset()
        init_loader.load_init_data("../database/init.json", LOCATOR)
        init_loader.load_init_data("data/finder_tests.json", LOCATOR)

    @classmethod
    def tearDownClass(self):
        dbgw.reset()

    def test_find_root_anon(self):
        handle = self.finder.find("/")
        self.assertEquals(handle.path, "/")
        self.assertEquals(handle.item_id, 1)
        self.assertEquals(handle.id_path, "1")
        self.assertEquals(handle.auth_level, item_finder.AuthLevels["reader"])
        self.assertIsNone(handle.user_handle)

    def test_find_non_absolute_path(self):
        handle = self.finder.find("does not exist")
        self.assertIsNone(handle.item_id)
        self.assertIsNone(handle.id_path)
        self.assertEquals(handle.auth_level, item_finder.AuthLevels["none"])


    def test_find_system_user(self):
        system_user_handle = self.finder.find_system_user()
        self.assertEquals(system_user_handle.path, "/users/system")
        self.assertTrue(system_user_handle.item_id > 1)
        self.assertEquals(system_user_handle.auth_level, item_finder.AuthLevels["reader"])
        self.assertIsNone(system_user_handle.user_handle)
        root_handle = self.finder.find("/")
        users_handle = self.finder.find("/users")
        self.assertEqual(system_user_handle.id_path,
                         str(root_handle.item_id) + "." +
                         str(users_handle.item_id) + "." +
                         str(system_user_handle.item_id))

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

    def test_users_edit_selves(self):
        user_paths = ["/paris/bob", "/milan/alice"]
        for user_path in user_paths:
            user_handle = self.finder.find(user_path)
            handle = self.finder.find(user_path, user_handle)
            # Users can edit themselves
            self.assertEqual(handle.auth_level, item_finder.AuthLevels["editor"])
            for other_user_path in user_paths:
                if other_user_path == user_path:
                    continue
                handle = self.finder.find(other_user_path, user_handle)
                # But can only read other users
                self.assertEqual(handle.auth_level, item_finder.AuthLevels["reader"])



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

    def test_get_path(self):
        alice_handle = self.finder.find("/milan/alice")
        path = self.finder.get_path(alice_handle.item_id)
        self.assertEquals("/milan/alice", path)

if __name__ == '__main__':
    unittest.main()