import postgresql


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

    def find_id(self, parent_id, name):
        sql = ("select "
               "id, id_path "
               "from public.items "
               "where "
               "parent_id = $1 and name = $2")
        ps = self.connection.prepare(sql)
        rows = ps(parent_id, name)
        if len(rows) == 0:
            return None
        else:
            return rows[0][0], rows[0][1]

