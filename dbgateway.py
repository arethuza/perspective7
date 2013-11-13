import postgresql
import json

class DbGateway:

    def __init__(self, locator):
        self.connection = postgresql.open(locator)

    def reset(self):
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

    def find_id(self, parent_id, name, select_auth=False):
        sql = ("select "
               "{0} "
               "from public.items "
               "where "
               "parent_id = $1 and name = $2")
        sql = sql.format("id, json_data->'auth'" if select_auth else "id, id_path")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name)
        if len(rows) == 0:
            return None, None
        item_id = rows[0][0]
        if not select_auth:
            id_path = rows[0][1]
            return item_id, id_path
        else:
            auth_json = rows[0][1]
            if auth_json is None:
                return item_id, None
            else:
                return item_id, json.loads(auth_json)

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


