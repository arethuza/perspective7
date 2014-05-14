import postgresql
import json
import performance as perf
import threading

thread_local = threading.local()

DBGW_KEY="dbgw"

locator = None


def get():
    dbgw = getattr(thread_local, DBGW_KEY, None)
    if dbgw is None:
        dbgw = DbGateway(locator)
        setattr(thread_local, DBGW_KEY, dbgw)
    return dbgw


def get_from_thread():
    return getattr(thread_local, DBGW_KEY, None)


class DbGateway:

    def __init__(self, locator):
        start = perf.start()
        self.connection = postgresql.open(locator)
        perf.end(__name__, start)

    def reset(self):
        self.connection.prepare("delete from public.file_blocks")()
        self.connection.prepare("delete from public.file_versions")()
        self.connection.prepare("delete from public.tokens")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("delete from public.items")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("select setval('items_id_seq', 0)")()

    def create_item_initial(self, parent_id, name, id_path, public_data, search_text):
        start = perf.start()
        sql = ("insert into public.items"
               "(parent_id, name, deletable, id_path, public_data, created_at, saved_at, search_text)"
               "values"
               "( $1, $2, false, "
               "  text2ltree(case when $1::int is null then '1' else $3::text || '.' || currval('items_id_seq') end),"
               "  $4, now(), now(), $5)"
               "returning id")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name, id_path, public_data, search_text)
        perf.end(__name__, start)
        return rows[0][0]

    def create_item(self, parent_id, name, id_path, type_id, type_path, public_data, created_by, search_text):
        start = perf.start()
        sql = ("insert into public.items"
               "(parent_id, name, id_path, type_id, type_path, public_data,"
               " created_at, created_by, saved_at, saved_by, search_text)"
               "values"
               "( $1, $2, "
               "  text2ltree($3::text || '.' || currval('items_id_seq')),"
               "  $4, text2ltree($5), $6, now(), $7, now(), $7, $8)"
               "returning id")
        ps = self.connection.prepare(sql)
        try:
            rows = ps(parent_id, name, id_path, type_id, type_path, public_data, created_by, search_text)
            return rows[0][0]
        except postgresql.exceptions.UniqueError as ex:
            return None
        finally:
            perf.end(__name__, start)

    def find_id(self, parent_id, name, select_auth=False):
        start = perf.start()
        sql = ("select "
               "{0} "
               "from public.items "
               "where "
               "parent_id = $1 and name = $2")
        sql = sql.format("id, public_data->'auth', version" if select_auth else "id, id_path, version")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name)
        if len(rows) == 0:
            return None, None, None
        item_id = rows[0][0]
        version = rows[0][2]
        perf.end2(__name__,  "find_id:" + str(select_auth), start)
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
        start = perf.start()
        sql = ("update public.items "
               "set type_id=$1, type_path=text2ltree($2), created_by=$3, saved_by=$3 "
               "where"
               " id=$4")
        ps = self.connection.prepare(sql)
        ps(type_id, type_id_path, user_id, item_id)
        perf.end(__name__, start)

    def load(self, item_id):
        start = perf.start()
        sql = ("select "
               "   type_item.public_data->>'item_class', "
               "   item_instance.name, "
               "   item_instance.public_data, "
               "   item_instance.created_at, "
               "   item_instance.saved_at, "
               "   item_instance.deletable "
               "from items item_instance inner join items type_item "
               "on item_instance.type_id = type_item.id "
               "and item_instance.id = $1")
        ps = self.connection.prepare(sql)
        rows=ps(item_id)
        perf.end(__name__, start)
        if len(rows) == 0:
            return None, None, None, None, None, None
        else:
            return rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5]

    def save_item_version(self, item_id):
        start = perf.start()
        sql = ("insert into item_versions "
               "select id, version, type_id, public_data, saved_at, saved_by "
               "from items "
               "where id=$1")
        ps = self.connection.prepare(sql)
        ps(item_id)
        perf.end(__name__, start)

    def update_item(self, item_id, public_data, user_id):
        start = perf.start()
        sql = ("update public.items "
               "set version=version+1, public_data=$2, saved_at=now(), saved_by=$3  "
               "where id=$1 "
               "returning version")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, public_data, user_id)
        perf.end(__name__, start)
        return rows[0][0]

    def get_item_id_path(self, item_id):
        start = perf.start()
        sql = "select id_path from items where id=$1"
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        perf.end(__name__, start)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None

    def get_item_name(self, item_id):
        start = perf.start()
        sql = "select name from items where id=$1"
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        perf.end(__name__, start)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None

    def update_private(self, item_id, private_data, user_id):
        start = perf.start()
        sql = ("update items "
               "set private_data=$2, saved_at=now(), saved_by=$3  "
               "where id=$1 ")
        ps = self.connection.prepare(sql)
        ps(item_id, private_data, user_id)
        perf.end(__name__, start)

    def get_private(self, item_id):
        start = perf.start()
        sql = ("select private_data from items "
               "where id=$1 ")
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        perf.end(__name__, start)
        return rows[0][0]

    def create_token(self, item_id, token_value, json_data, expires_at):
        start = perf.start()
        sql = ("insert into tokens "
               "(item_id, token_value, json_data, created_at, expires_at) "
               "values "
               "($1, $2::text, $3, now(), $4::text::timestamp)")
        ps = self.connection.prepare(sql)
        ps(item_id, token_value, json_data, expires_at)
        perf.end(__name__, start)

    def find_token(self, token_value):
        start = perf.start()
        sql = ("select item_id, json_data from tokens "
               "where token_value=$1 and expires_at > now()")
        ps = self.connection.prepare(sql)
        rows = ps(token_value)
        perf.end(__name__, start)
        if len(rows) > 0:
            return rows[0][0], rows[0][1]
        else:
            return None, None

    def delete_token(self, token_value):
        start = perf.start()
        sql = "delete from tokens where token_value=$1"
        ps = self.connection.prepare(sql)
        ps(token_value)
        perf.end(__name__, start)

    def count_items(self):
        start = perf.start()
        sql = "select count(id) from items"
        ps = self.connection.prepare(sql)
        rows = ps()
        perf.end(__name__, start)
        return rows[0][0]

    def create_file_version(self, item_id, previous_version, user_id):
        start = perf.start()
        sql = ("insert into file_versions "
               "(item_id, file_version, previous_version, created_at, created_by) "
               "select $1, coalesce(max(file_version) + 1, 0), $2, now(), $3 from file_versions "
               "returning file_versions.file_version")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, previous_version, user_id)
        perf.end(__name__, start)
        return rows[0][0]

    def copy_file_blocks(self, item_id, file_version, previous_version):
        start = perf.start()
        sql = ("insert into file_blocks"
               "(item_id, file_version, block_number, data_file_version, length, hash, created_at) "
               "select item_id, $3, block_number, $2, length, hash, now()"
               "from file_blocks "
               "where item_id = $1 and file_version = $2")
        ps = self.connection.prepare(sql)
        perf.end(__name__, start)
        rows = ps(item_id, previous_version, file_version)

    def create_file_block(self, item_id, file_version, block_number, block_hash, block_data):
        start = perf.start()
        sql = ("insert into file_blocks "
               "(item_id, file_version, block_number, length, hash, created_at, data) "
               "values ($1, $2, $3, $4, $5, now(), $6)")
        ps = self.connection.prepare(sql)
        perf.end(__name__, start)
        ps(item_id, file_version, block_number, len(block_data), block_hash, block_data)

    def update_file_block(self, item_id, file_version, block_number, block_hash, block_data):
        start = perf.start()
        sql = ("update file_blocks "
               "set length=$4, hash=$5, created_at=now(), data=$6 "
               "where item_id=$1 and file_version=$2 and block_number=$3")
        ps = self.connection.prepare(sql)
        perf.end(__name__, start)
        ps(item_id, file_version, block_number, len(block_data), block_hash, block_data)

    def get_file_block_data(self, item_id, file_version, block_number):
        start = perf.start()
        sql = ("select data "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 and block_number=$3")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version, block_number)
        perf.end(__name__, start)
        return rows[0][0]

    def get_file_block_hash(self, item_id, file_version, block_number):
        start = perf.start()
        sql = ("select hash "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 and block_number=$3")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version, block_number)
        perf.end(__name__, start)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None

    def get_file_block_data_file_version(self, item_id, file_version, block_number):
        start = perf.start()
        sql = ("select data_file_version "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 and block_number=$3")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version, block_number)
        perf.end(__name__, start)
        return rows[0][0]

    def list_file_blocks(self, item_id, file_version):
        start = perf.start()
        sql = ("select block_number, data_file_version, length, file_blocks.hash, file_blocks.created_at "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 "
               "order by block_number asc")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version)
        perf.end(__name__, start)
        return rows

    def delete_file_block(self, item_id, file_version, block_number):
        start = perf.start()
        sql = ("delete "
               "from file_blocks "
               "where item_id=$1 and file_version=$2 and block_number=$3")
        ps = self.connection.prepare(sql)
        ps(item_id, file_version, block_number)
        perf.end(__name__, start)

    def list_file_versions(self, item_id):
        start = perf.start()
        sql = ("select "
               "   file_version, previous_version, length, hash, created_at, created_by "
               "from file_versions "
               "where item_id=$1 "
               "order by file_version asc")
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        perf.end(__name__, start)
        return rows

    def get_file_version(self, item_id, file_version):
        start = perf.start()
        sql = ("select length, hash, previous_version from file_versions "
               "where item_id=$1 and file_version=$2")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, file_version)
        perf.end(__name__, start)
        if len(rows) > 0:
            return rows[0][0], rows[0][1], rows[0][2]
        else:
            return None, None, None, None

    def set_file_version_length_hash(self, item_id, file_version, file_length, file_hash):
        start = perf.start()
        sql = ("update file_versions "
               "set length=$3, hash=$4 "
               "where item_id=$1 and file_version=$2")
        ps = self.connection.prepare(sql)
        ps(item_id, file_version, file_length, file_hash)
        perf.end(__name__, start)

    def delete_item(self, item_id):
        start = perf.start()
        sql = "delete from items where id=$1 and deletable=true returning id"
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        perf.end(__name__, start)
        return len(rows) > 0

    def list_child_items(self, item_id):
        start = perf.start()
        sql = "select id, name, type_id, public_data from items where parent_id=$1 order by name"
        ps = self.connection.prepare(sql)
        rows = ps(item_id)
        perf.end(__name__, start)
        return rows

    def set_item_name(self, item_id, name):
        start = perf.start()
        sql = "update items set name=$2 where id=$1"
        ps = self.connection.prepare(sql)
        ps(item_id, name)
        perf.end(__name__, start)

    def get_first_parent_of_type(self, item_id, type_id):
        start = perf.start()
        sql = ("with recursive search_parents(id, type_id, parent_id, height) as ( "
               "       select id, type_id, parent_id, 1 from items where id=$1 "
               "   union "
               "       select it.id, it.type_id, it.parent_id, height + 1 "
               "       from items it "
               "       join search_parents parents on parents.parent_id = it.id) "
               "select id from search_parents where type_id=$2 and id != $1 order by height asc limit 1")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, type_id)
        perf.end(__name__, start)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None







