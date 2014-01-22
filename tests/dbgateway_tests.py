import unittest
import dbgateway
import time
import datetime

LOCATOR = "pq://postgres:password@localhost/perspective"
dbgw = dbgateway.DbGateway(LOCATOR)

class DbGatewayTests(unittest.TestCase):

    def setUp(self):
        dbgw.reset()

    def tearDown(self):
        self.setUp()

    def test_delete_all(self):
        dbgw.reset()

    def test_create_item_initial(self):
        item_id = dbgw.create_item_initial(None, "foo", "_", "{ \"raz\": 1 }", "raz")
        self.assertEquals(item_id, 1)

    def test_create_item_initial_and_find_id(self):
        dbgw.create_item_initial(None, "", None, "{ \"raz\": 1 }", "raz")
        dbgw.create_item_initial(1, "foo", "1", "{ \"bar\": 1 }", "foo")
        item_id, item_id_path, version = dbgw.find_id(1, "foo")
        self.assertTrue(item_id > 1)
        self.assertEquals(item_id_path, "1.2")
        self.assertEqual(version, 0)

    def test_load(self):
        item_id = dbgw.create_item_initial(None, "test item", None, "{}", "")
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        dbgw.set_item_type_user(item_id, type_id, "1", user_id)
        class_name, name, data, created_at, saved_at = dbgw.load(item_id)
        self.assertEquals(class_name, "foo")
        self.assertEquals(name, "test item")
        self.assertEquals(data, "{}")

    def test_create_item(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        item_id, item_id_path, version = dbgw.find_id(3, "bar")
        self.assertTrue(item_id > 1)
        self.assertEquals(item_id_path, "6.7." + str(item_id))
        self.assertEqual(version, 0)

    def test_save_item_version(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        dbgw.save_item_version(item_id)

    def test_update_item(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        dbgw.update_item(item_id, "{}", user_id)

    def test_create_find_token(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        future_date = (datetime.datetime.fromtimestamp(int(time.time())) + datetime.timedelta(days=10)).isoformat()
        dbgw.create_token(item_id, "foo", future_date)
        self.assertEqual(dbgw.find_token("foo"), item_id)
        dbgw.delete_token("foo")
        self.assertIsNone(dbgw.find_token("foo"))

    def test_count_items(self):
        self.assertEquals(dbgw.count_items(), 0)
        dbgw.create_item_initial(None, "foo", "_", "{ \"raz\": 1 }", "raz")
        self.assertEquals(dbgw.count_items(), 1)
        dbgw.create_item_initial(None, "bar", "_", "{ \"raz\": 1 }", "raz")
        self.assertEquals(dbgw.count_items(), 2)

    def test_create_file_version_blocks(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        file_version_id = dbgw.create_file_version(item_id, 0, 40, "abc", user_id)
        dbgw.create_file_block(file_version_id, 0, "0123", b'\xff\xf8\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(file_version_id, 1, "0124", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(file_version_id, 2, "0125", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        dbgw.set_item_file_version(item_id, file_version_id)
        pass



if __name__ == '__main__':
    unittest.main()