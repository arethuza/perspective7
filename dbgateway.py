import postgresql
import json

class DbGateway:

    def __init__(self, locator):
        self.connection = postgresql.open(locator)

    def reset(self):
        self.connection.prepare("delete from public.file_blocks")()
        self.connection.prepare("delete from public.file_versions")()
        self.connection.prepare("delete from public.tokens")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("delete from public.items")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("select setval('items_id_seq', 0)")()

    def create_item_initial(self, parent_id, name, id_path, json_data, search_text):
        sql = ("insert into public.items"
               "(parent_id, name, id_path, json_data, created_at, saved_at, search_text)"
               "values"
               "( $1, $2, "
               "  text2ltree(case when $1::int is null then '1' else $3::text || '.' || currval('items_id_seq') end),"
               "  $4, now(), now(), $5)"
               "returning id")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name, id_path, json_data, search_text)
        return rows[0][0]

    def create_item(self, parent_id, name, id_path, type_id, type_path, json_data, created_by, search_text):
        sql = ("insert into public.items"
               "(parent_id, name, id_path, type_id, type_path, json_data,"
               " created_at, created_by, saved_at, saved_by, search_text)"
               "values"
               "( $1, $2, "
               "  text2ltree($3::text || '.' || currval('items_id_seq')),"
               "  $4, text2ltree($5), $6, now(), $7, now(), $7, $8)"
               "returning id")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name, id_path, type_id, type_path, json_data, created_by, search_text)
        return rows[0][0]

    def find_id(self, parent_id, name, select_auth=False):
        sql = ("select "
               "{0} "
               "from public.items "
               "where "
               "parent_id = $1 and name = $2")
        sql = sql.format("id, json_data->'auth', version" if select_auth else "id, id_path, version")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name)
        if len(rows) == 0:
            return None, None, None
        item_id = rows[0][0]
        version = rows[0][2]
        if not select_auth:
            id_path = rows[0][1]
            return item_id, id_path, version
        else:
            auth_json = rows[0][1]
            if auth_json is None:
                return item_id, None, version
            else:
                return item_id, json.loads(auth_json), version

    def set_item_type_user(self, item_id, type_id, type_id_path, user_id):
        sql = ("update public.items "
               "set type_id=$1, type_path=text2ltree($2), created_by=$3, saved_by=$3 "
               "where"
               " id=$4")
        ps = self.connection.prepare(sql)
        ps(type_id, type_id_path, user_id, item_id)

    def load(self, item_id):
        sql = ("select "
               "   type_item.json_data->>'item_class', "
               "   item_instance.name, "
               "   item_instance.json_data, "
               "   item_instance.created_at, "
               "   item_instance.saved_at "
               "from items item_instance inner join items type_item "
               "on item_instance.type_id = type_item.id "
               "and item_instance.id = $1")
        ps = self.connection.prepare(sql)
        rows=ps(item_id)
        if len(rows) == 0:
            return None, None, None, None, None
        else:
            return rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4]

    def save_item_version(self, item_id):
        sql = ("insert into public.item_versions "
               "select id, version, type_id, json_data, saved_at, saved_by "
               "from public.items "
               "where id=$1")
        ps = self.connection.prepare(sql)
        ps(item_id)

    def update_item(self, item_id, json_data, user_id):
        sql = ("update public.items "
               "set version=version+1, json_data=$2, saved_at=now(), saved_by=$3  "
               "where id=$1 "
               "returning version")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, json_data, user_id)
        return rows[0][0]

    def get_item_id_path(self, item_id):
        sql = "select id_path from items where id=$1"
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None

    def get_item_name(self, item_id):
        sql = "select name from items where id=$1"
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None

    def create_token(self, item_id, token_value, json_data, expires_at):
        sql = ("insert into tokens "
               "(item_id, token_value, json_data, created_at, expires_at) "
               "values "
               "($1, $2::text, $3, now(), $4::text::timestamp)")
        ps = self.connection.prepare(sql)
        ps(item_id, token_value, json_data, expires_at)

    def find_token(self, token_value):
        sql = ("select item_id, json_data from tokens "
               "where token_value=$1 and expires_at > now()")
        ps = self.connection.prepare(sql)
        rows = ps(token_value)
        if len(rows) > 0:
            return rows[0][0], rows[0][1]
        else:
            return None, None

    def delete_token(self, token_value):
        sql = "delete from tokens where token_value=$1"
        ps = self.connection.prepare(sql)
        ps(token_value)

    def count_items(self):
        sql = "select count(id) from items"
        ps = self.connection.prepare(sql)
        rows = ps()
        return rows[0][0]

    def create_file_version(self, item_id, previous_version, user_id):
        sql = ("insert into file_versions "
               "(item_id, file_version, previous_version, created_at, created_by) "
               "select $1, coalesce(max(file_version) + 1, 0), $2, now(), $3 from file_versions "
               "returning file_versions.file_version")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, previous_version, user_id)
        return rows[0][0]

    def create_file_block(self, item_id, file_version, block_number, block_hash, block_data):
        sql = ("insert into file_blocks "
               "(item_id, file_version, block_number, hash, created_at, data) "
               "values ($1, $2, $3, $4, now(), $5)")
        ps = self.connection.prepare(sql)
        ps(item_id, file_version, block_number, block_hash, block_data)

    def get_file_block_data(self, item_id, file_version, block_number):
        sql = ("select data "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 and block_number=$3")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version, block_number)
        return rows[0][0]

    def list_file_blocks(self, item_id, file_version):
        sql = ("select block_number, length(file_blocks.data), file_blocks.hash, file_blocks.created_at "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 "
               "order by block_number asc")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version)
        return rows

    def list_file_versions(self, item_id):
        sql = ("select "
               "   file_version, previous_version, length, hash, created_at, created_by "
               "from file_versions "
               "where item_id=$1 "
               "order by file_version asc")
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        return rows

    def get_file_version(self, item_id, file_version):
        sql = ("select length, hash, previous_version from file_versions "
               "where item_id=$1 and file_version=$2")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version)
        if len(rows) > 0:
            return rows[0][0], rows[0][1], rows[0][2]
        else:
            return None, None, None, None

    def set_file_version_length_hash(self, item_id, file_version, file_length, file_hash):
        sql = ("update file_versions "
               "set length=$3, hash=$4 "
               "where item_id=$1 and file_version=$2")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version, file_length, file_hash)










