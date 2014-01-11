import postgresql
import json

class DbGateway:

    def __init__(self, locator):
        self.connection = postgresql.open(locator)

    def reset(self):
        self.connection.prepare("delete from public.tokens")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("delete from public.items")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("delete from public.item_binary_data")()
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
        sql = ("select type_item.json_data->>'item_class',item_instance.json_data "
               "from items item_instance inner join items type_item "
               "on item_instance.type_id = type_item.id "
               "and item_instance.id = $1")
        ps = self.connection.prepare(sql)
        rows=ps(item_id)
        if len(rows) == 0:
            return None, None
        else:
            return rows[0][0], rows[0][1]

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
               "where id=$1")
        ps = self.connection.prepare(sql)
        ps(item_id, json_data, user_id)

    def create_token(self, item_id, token_value, expires_at):
        sql = ("insert into tokens "
               "(item_id, token_value, created_at, expires_at) "
               "values "
               "($1, $2::text, now(), $3::text::timestamp)")
        ps = self.connection.prepare(sql)
        ps(item_id, token_value, expires_at)

    def find_token(self, item_id, token_value):
        sql = ("select count(item_id) from tokens "
               "where item_id=$1 and token_value=$2 and expires_at > now()")
        ps = self.connection.prepare(sql)
        rows = ps(item_id, token_value)
        count = rows[0][0]
        return count > 0

    def delete_token(self, token_value):
        sql = "delete from tokens where token_value=$1"
        ps = self.connection.prepare(sql)
        ps(token_value)




