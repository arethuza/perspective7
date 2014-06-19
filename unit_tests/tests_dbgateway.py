import unittest
import dbgateway
import time
import datetime
import json

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
        type_id, name, data, created_at, saved_at, deletable = dbgw.load(item_id)
        self.assertEquals(type_id, 2)
        self.assertEquals(name, "test item")
        self.assertEquals(data, "{}")
        self.assertFalse(deletable)

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
        version = dbgw.update_item(item_id, "{}", user_id)
        self.assertEquals(version, 1)
        version = dbgw.update_item(item_id, "{ \"foo\":3 }", user_id)
        self.assertEquals(version, 2)

    def test_update_get_private_data(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        dbgw.update_private(item_id, "{\"secret\": \"boo\"}", user_id)
        private_data = json.loads(dbgw.get_private(item_id))
        self.assertEquals(1, len(private_data))
        self.assertEquals("boo", private_data["secret"])
        dbgw.update_private(item_id, None, user_id)
        self.assertIsNone(dbgw.get_private(item_id))

    def test_create_find_token(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        future_date = (datetime.datetime.fromtimestamp(int(time.time())) + datetime.timedelta(days=10)).isoformat()
        dbgw.create_token(item_id, "foo", "{}", future_date)
        token_item_id, token_json_data = dbgw.find_token("foo")
        self.assertEqual(item_id, token_item_id)
        self.assertEqual(token_json_data, "{}")
        dbgw.delete_token("foo")
        token_item_id, token_json_data = dbgw.find_token("foo")
        self.assertIsNone(token_item_id)
        self.assertIsNone(token_json_data)

    def test_count_items(self):
        self.assertEquals(dbgw.count_items(), 0)
        dbgw.create_item_initial(None, "foo", "_", "{ \"raz\": 1 }", "raz")
        self.assertEquals(dbgw.count_items(), 1)
        dbgw.create_item_initial(None, "bar", "_", "{ \"raz\": 1 }", "raz")
        self.assertEquals(dbgw.count_items(), 2)

    def test_create_file_version_blocks(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        user_id2 = dbgw.create_item_initial(None, "test user2", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        file_version = dbgw.create_file_version(item_id, None, user_id)
        self.assertEquals(file_version, 0)
        dbgw.create_file_block(item_id, file_version, 0, "0123", b'\xff\xf8\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(item_id, file_version, 1, "0124", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(item_id, file_version, 2, "0125", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        data = dbgw.get_file_block_data(item_id, file_version, 0)
        self.assertIsNotNone(dbgw.get_file_block_hash(item_id, file_version, 0))
        self.assertIsNone(dbgw.get_file_block_hash(item_id, file_version, 3))
        self.assertEquals(len(data), 8)
        data = dbgw.get_file_block_data(item_id, file_version, 1)
        self.assertEquals(len(data), 10)
        data = dbgw.get_file_block_data(item_id, file_version, 2)
        self.assertEquals(len(data), 13)
        blocks_list = dbgw.list_file_blocks(item_id, file_version)
        self.assertEquals(len(blocks_list), 3)
        self.assertEquals(blocks_list[0][0], 0)
        self.assertEquals(blocks_list[1][0], 1)
        self.assertEquals(blocks_list[2][0], 2)
        self.assertIsNone(blocks_list[0][1])
        self.assertIsNone(blocks_list[1][1])
        self.assertIsNone(blocks_list[2][1])
        self.assertEquals(blocks_list[0][2], 8)
        self.assertEquals(blocks_list[1][2], 10)
        self.assertEquals(blocks_list[2][2], 13)
        self.assertEquals(blocks_list[0][3], "0123")
        self.assertEquals(blocks_list[1][3], "0124")
        self.assertEquals(blocks_list[2][3], "0125")
        file_version = dbgw.create_file_version(item_id, 0, user_id2)
        self.assertEquals(file_version, 1)
        file_versions = dbgw.list_file_versions(item_id)
        self.assertEquals(len(file_versions), 2)
        self.assertEquals(file_versions[0][0], 0)
        self.assertEquals(file_versions[0][1], None)
        self.assertEquals(file_versions[0][2], 0)
        self.assertEquals(file_versions[0][3], None)
        self.assertIsNotNone(file_versions[0][4])
        self.assertEquals(file_versions[0][5], user_id)
        self.assertEquals(file_versions[1][0], 1)
        self.assertEquals(file_versions[1][1], 0)
        self.assertEquals(file_versions[1][2], 0)
        self.assertEquals(file_versions[1][3], None)
        self.assertIsNotNone(file_versions[1][4])
        self.assertEquals(file_versions[1][5], user_id2)

    def test_update_file_block(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        file_version = dbgw.create_file_version(item_id, None, user_id)
        dbgw.create_file_block(item_id, file_version, 0, "0123", b'0' * 10)
        self.assertEquals(dbgw.get_file_block_data(item_id, file_version, 0), b'0' * 10)
        dbgw.update_file_block(item_id, file_version, 0, "4567", b'1' * 20)
        self.assertEquals(dbgw.get_file_block_data(item_id, file_version, 0), b'1' * 20)
        dbgw.update_file_block(item_id, file_version, 0, "78910", b'2' * 40)
        self.assertEquals(dbgw.get_file_block_data(item_id, file_version, 0), b'2' * 40)
        blocks_list = dbgw.list_file_blocks(item_id, file_version)
        self.assertEquals(len(blocks_list), 1)
        self.assertEquals(blocks_list[0][0], 0)
        self.assertIsNone(blocks_list[0][1])
        self.assertEquals(blocks_list[0][2], 40)
        self.assertEquals(blocks_list[0][3], "78910")

    def test_copy_file_blocks(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        user_id2 = dbgw.create_item_initial(None, "test user2", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        # Create first version of file and populate some blocks
        file_version = dbgw.create_file_version(item_id, None, user_id)
        self.assertEquals(file_version, 0)
        dbgw.create_file_block(item_id, file_version, 0, "0123", b'\xff\xf8\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(item_id, file_version, 1, "0124", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(item_id, file_version, 2, "0125", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        data = dbgw.get_file_block_data(item_id, file_version, 0)
        # Create second version of file and populate some blocks
        file_version = dbgw.create_file_version(item_id, 0, user_id2)
        # Copy the existing blocks to the new version
        dbgw.copy_file_blocks(item_id, file_version, 0)
        # Check the blocks
        blocks = dbgw.list_file_blocks(item_id, file_version)
        self.assertEquals(len(blocks), 3)
        # Block numbers
        self.assertEquals(blocks[0][0], 0)
        self.assertEquals(blocks[1][0], 1)
        self.assertEquals(blocks[2][0], 2)
        # File version where data actually resides
        self.assertEquals(0, blocks[0][1])
        self.assertEquals(0, blocks[1][1])
        self.assertEquals(0, blocks[2][1])
        # Block lengths
        self.assertEquals(blocks[0][2], 8)
        self.assertEquals(blocks[1][2], 10)
        self.assertEquals(blocks[2][2], 13)
        # Update block 1
        dbgw.update_file_block(item_id, file_version, 1, "foo", b'\77' * 45)
        # Check the blocks
        blocks = dbgw.list_file_blocks(item_id, file_version)
        self.assertEquals(len(blocks), 3)
        # Block numbers
        self.assertEquals(blocks[0][0], 0)
        self.assertEquals(blocks[1][0], 1)
        self.assertEquals(blocks[2][0], 2)
        # File version where data actually resides
        self.assertEquals(blocks[0][1], 0)
        self.assertIsNone(blocks[1][1])
        self.assertEquals(blocks[2][1], 0)
        # Block lengths
        self.assertEquals(blocks[0][2], 8)
        self.assertEquals(blocks[1][2], 45)
        self.assertEquals(blocks[2][2], 13)

    def test_list_file_version_blocks(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        # Create version 0 of file and populate some blocks - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertEquals(0, dbgw.create_file_version(item_id, None, user_id))
        dbgw.create_file_block(item_id, 0, 0, "0123", b'\xff\xf8\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(item_id, 0, 1, "0124", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00')
        dbgw.create_file_block(item_id, 0, 2, "0125", b'\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        blocks = dbgw.list_file_blocks(item_id, 0)
        self.assertEquals(len(blocks), 3)
        # Block numbers
        self.assertEquals(blocks[0][0], 0)
        self.assertEquals(blocks[1][0], 1)
        self.assertEquals(blocks[2][0], 2)
        # File version where data actually resides
        self.assertIsNone(blocks[0][1])
        self.assertIsNone(blocks[1][1])
        self.assertIsNone(blocks[2][1])
        # Block lengths
        self.assertEquals(blocks[0][2], 8)
        self.assertEquals(blocks[1][2], 10)
        self.assertEquals(blocks[2][2], 13)
        # Create version 1 of file, copy blocks and update one block - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertEquals(1, dbgw.create_file_version(item_id, 0, user_id))
        dbgw.copy_file_blocks(item_id, 1, 0)
        dbgw.update_file_block(item_id, 1, 1, "abcd", b'\xff' * 34)
        blocks = dbgw.list_file_blocks(item_id, 1)
        self.assertEquals(len(blocks), 3)
        # Block numbers
        self.assertEquals(blocks[0][0], 0)
        self.assertEquals(blocks[1][0], 1)
        self.assertEquals(blocks[2][0], 2)
        # File version where data actually resides
        self.assertEquals(0, blocks[0][1])
        self.assertIsNone(   blocks[1][1])
        self.assertEquals(0, blocks[2][1])
        # Block lengths
        self.assertEquals(blocks[0][2], 8)
        self.assertEquals(blocks[1][2], 34)
        self.assertEquals(blocks[2][2], 13)
        # Create version 2 of file, copy blocks and update two blocks - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertEquals(2, dbgw.create_file_version(item_id, 1, user_id))
        dbgw.copy_file_blocks(item_id, 2, 1)
        dbgw.update_file_block(item_id, 2, 0, "hijk", b'\x33' * 123)
        dbgw.update_file_block(item_id, 2, 1, "abcd", b'\x77' * 234)
        blocks = dbgw.list_file_blocks(item_id, 2)
        self.assertEquals(len(blocks), 3)
        # Block numbers
        self.assertEquals(blocks[0][0], 0)
        self.assertEquals(blocks[1][0], 1)
        self.assertEquals(blocks[2][0], 2)
        # File version where data actually resides
        self.assertIsNone(   blocks[0][1])
        self.assertIsNone(   blocks[1][1])
        self.assertEquals(0, blocks[2][1])
        # Block lengths
        self.assertEquals(blocks[0][2], 123)
        self.assertEquals(blocks[1][2], 234)
        self.assertEquals(blocks[2][2], 13)
        # Create version 3 of file, copy blocks and update one block - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertEquals(3, dbgw.create_file_version(item_id, 2, user_id))
        dbgw.copy_file_blocks(item_id, 3, 2)
        dbgw.update_file_block(item_id, 3, 2, "hijk", b'\x99' * 1021)
        blocks = dbgw.list_file_blocks(item_id, 3)
        self.assertEquals(len(blocks), 3)
        # Block numbers
        self.assertEquals(blocks[0][0], 0)
        self.assertEquals(blocks[1][0], 1)
        self.assertEquals(blocks[2][0], 2)
        # File version where data actually resides
        self.assertEquals(2, blocks[0][1])
        self.assertEquals(2, blocks[1][1])
        self.assertIsNone(   blocks[2][1])
        # Block lengths
        self.assertEquals(blocks[0][2], 123)
        self.assertEquals(blocks[1][2], 234)
        self.assertEquals(blocks[2][2], 1021)
        # Now have 4 versions
        # Version 0 -> 0
        version_blocks = dbgw.list_file_version_blocks(item_id, 0, 0)
        self.assertEquals(len(version_blocks), 3)
        # File versions
        self.assertEquals(0, version_blocks[0][0])
        self.assertEquals(0, version_blocks[1][0])
        self.assertEquals(0, version_blocks[2][0])
        # Block numbers
        self.assertEquals(0, version_blocks[0][1])
        self.assertEquals(1, version_blocks[1][1])
        self.assertEquals(2, version_blocks[2][1])
        # File version where data actually resides
        self.assertIsNone(version_blocks[0][2])
        self.assertIsNone(version_blocks[1][2])
        self.assertIsNone(version_blocks[2][2])
        # Version 0 -> 1
        version_blocks = dbgw.list_file_version_blocks(item_id, 0, 1)
        self.assertEquals(len(version_blocks), 6)
        # File versions
        self.assertEquals(0, version_blocks[0][0])
        self.assertEquals(0, version_blocks[1][0])
        self.assertEquals(0, version_blocks[2][0])
        self.assertEquals(1, version_blocks[3][0])
        self.assertEquals(1, version_blocks[4][0])
        self.assertEquals(1, version_blocks[5][0])
        # Block numbers
        self.assertEquals(0, version_blocks[0][1])
        self.assertEquals(1, version_blocks[1][1])
        self.assertEquals(2, version_blocks[2][1])
        self.assertEquals(0, version_blocks[3][1])
        self.assertEquals(1, version_blocks[4][1])
        self.assertEquals(2, version_blocks[5][1])
        # File version where data actually resides
        self.assertIsNone(   version_blocks[0][2])
        self.assertIsNone(   version_blocks[1][2])
        self.assertIsNone(   version_blocks[2][2])
        self.assertEquals(0, version_blocks[3][2])
        self.assertIsNone(   version_blocks[4][2]) # Only modified block 1 in version 1
        self.assertEquals(0, version_blocks[5][2])
        # Version 0 -> 2
        version_blocks = dbgw.list_file_version_blocks(item_id, 0, 2)
        self.assertEquals(len(version_blocks), 9)
        # File versions
        self.assertEquals(0, version_blocks[0][0])
        self.assertEquals(0, version_blocks[1][0])
        self.assertEquals(0, version_blocks[2][0])
        self.assertEquals(1, version_blocks[3][0])
        self.assertEquals(1, version_blocks[4][0])
        self.assertEquals(1, version_blocks[5][0])
        self.assertEquals(2, version_blocks[6][0])
        self.assertEquals(2, version_blocks[7][0])
        self.assertEquals(2, version_blocks[8][0])
        # Block numbers
        self.assertEquals(0, version_blocks[0][1])
        self.assertEquals(1, version_blocks[1][1])
        self.assertEquals(2, version_blocks[2][1])
        self.assertEquals(0, version_blocks[3][1])
        self.assertEquals(1, version_blocks[4][1])
        self.assertEquals(2, version_blocks[5][1])
        self.assertEquals(0, version_blocks[6][1])
        self.assertEquals(1, version_blocks[7][1])
        self.assertEquals(2, version_blocks[8][1])
        # File version where data actually resides
        self.assertIsNone(   version_blocks[0][2])
        self.assertIsNone(   version_blocks[1][2])
        self.assertIsNone(   version_blocks[2][2])
        self.assertEquals(0, version_blocks[3][2])
        # Only modified block 1 in version 1
        self.assertIsNone(   version_blocks[4][2])
        self.assertEquals(0, version_blocks[5][2])
        # Modified block 0 and 1 in version 2
        self.assertIsNone(   version_blocks[6][2])
        self.assertIsNone(   version_blocks[7][2])
        self.assertEquals(0, version_blocks[8][2])
        # Version 0 -> 3
        version_blocks = dbgw.list_file_version_blocks(item_id, 0, 3)
        self.assertEquals(len(version_blocks), 12)
        # File versions
        self.assertEquals(0, version_blocks[0][0])
        self.assertEquals(0, version_blocks[1][0])
        self.assertEquals(0, version_blocks[2][0])
        self.assertEquals(1, version_blocks[3][0])
        self.assertEquals(1, version_blocks[4][0])
        self.assertEquals(1, version_blocks[5][0])
        self.assertEquals(2, version_blocks[6][0])
        self.assertEquals(2, version_blocks[7][0])
        self.assertEquals(2, version_blocks[8][0])
        self.assertEquals(3, version_blocks[9][0])
        self.assertEquals(3, version_blocks[10][0])
        self.assertEquals(3, version_blocks[11][0])
        # Block numbers
        self.assertEquals(0, version_blocks[0][1])
        self.assertEquals(1, version_blocks[1][1])
        self.assertEquals(2, version_blocks[2][1])
        self.assertEquals(0, version_blocks[3][1])
        self.assertEquals(1, version_blocks[4][1])
        self.assertEquals(2, version_blocks[5][1])
        self.assertEquals(0, version_blocks[6][1])
        self.assertEquals(1, version_blocks[7][1])
        self.assertEquals(2, version_blocks[8][1])
        self.assertEquals(0, version_blocks[9][1])
        self.assertEquals(1, version_blocks[10][1])
        self.assertEquals(2, version_blocks[11][1])
        # File version where data actually resides
        self.assertIsNone(   version_blocks[0][2])
        self.assertIsNone(   version_blocks[1][2])
        self.assertIsNone(   version_blocks[2][2])
        self.assertEquals(0, version_blocks[3][2])
        # Only modified block 1 in version 1
        self.assertIsNone(   version_blocks[4][2])
        self.assertEquals(0, version_blocks[5][2])
        # Modified block 0 and 1 in version 2
        self.assertIsNone(   version_blocks[6][2])
        self.assertIsNone(   version_blocks[7][2])
        self.assertEquals(0, version_blocks[8][2])
        # Modified block 2 in version 3
        self.assertEquals(2, version_blocks[9][2])
        self.assertEquals(2, version_blocks[10][2])
        self.assertIsNone(   version_blocks[11][2])



    def test_get_item_id_path(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        user_id2 = dbgw.create_item_initial(None, "test user2", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        id_path = dbgw.get_item_id_path(item_id)
        self.assertEquals("6.7.4", id_path)

    def test_get_item_name(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        user_id2 = dbgw.create_item_initial(None, "test user2", None, "{}", "")
        item_id = dbgw.create_item(3, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        name = dbgw.get_item_name(item_id)
        self.assertEquals("bar", name)

    def test_delete_item(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id_foo = dbgw.create_item(None, "foo", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        item_id_bar = dbgw.create_item(item_id_foo, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        item_id_raz = dbgw.create_item(item_id_bar, "raz", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        self.assertEquals(item_id_bar, dbgw.find_id(item_id_foo, "bar")[0])
        self.assertEquals(item_id_raz, dbgw.find_id(item_id_bar, "raz")[0])
        did_delete = dbgw.delete_item(item_id_bar)
        self.assertTrue(did_delete)
        self.assertIsNone(dbgw.find_id(item_id_foo, "bar")[0])
        self.assertIsNone(dbgw.find_id(item_id_bar, "raz")[0])

    def test_list_child_items(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id_foo = dbgw.create_item(None, "foo", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        item_id_bar = dbgw.create_item(item_id_foo, "bar", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        item_id_raz = dbgw.create_item(item_id_foo, "raz", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        list = dbgw.list_child_items(item_id_foo)
        self.assertEquals(2, len(list))
        self.assertEquals("bar", list[0][1])
        self.assertEquals("raz", list[1][1])

    def test_set_item_name(self):
        type_id = dbgw.create_item_initial(None, "test type", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id_foo = dbgw.create_item(None, "foo", "6.7", type_id, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        dbgw.set_item_name(item_id_foo, "bar")
        self.assertEquals("bar", dbgw.get_item_name(item_id_foo))

    def test_get_first_parent_of_type(self):
        type_id1 = dbgw.create_item_initial(None, "test type 1", None, "{ \"item_class\": \"foo\" }", "")
        type_id2 = dbgw.create_item_initial(None, "test type 2", None, "{ \"item_class\": \"foo\" }", "")
        user_id = dbgw.create_item_initial(None, "test user", None, "{}", "")
        item_id_foo = dbgw.create_item(None, "foo", "6.7", type_id1, "3.4", "{ \"raz\": 1 }", user_id, "one banana")
        item_id_bar = dbgw.create_item(item_id_foo, "bar", "6.7", type_id2, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        item_id_raz = dbgw.create_item(item_id_bar, "raz", "6.7", type_id2, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        item_id_bob = dbgw.create_item(item_id_raz, "bob", "6.7", type_id2, "3.4", "{ \"raz\": 1 }", user_id, "one ban")
        self.assertEquals(item_id_foo, dbgw.get_first_parent_of_type(item_id_raz, type_id1))
        self.assertEquals(item_id_raz, dbgw.get_first_parent_of_type(item_id_bob, type_id2))

if __name__ == '__main__':
    unittest.main()