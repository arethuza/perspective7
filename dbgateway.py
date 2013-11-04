import postgresql


class DbGateway:
    def __init__(self, locator):
        self.connection = postgresql.open(locator)

    def delete_all(self):
        self.connection.prepare("delete from public.items")()
        self.connection.prepare("delete from public.item_versions")()
        self.connection.prepare("delete from public.item_binary_data")()

    def create_item_bootstrap(self, parent_id, name, id_path, json_data, search_text):
        sql = ("insert into public.items"
               "(parent_id, name, id_path, json_data, created_at, saved_at, search_text)"
               "values"
               "($1, $2, text2ltree($3), $4, now(), now(), $5)")
        ps = self.connection.prepare(sql)
        ps(parent_id, name, id_path, json_data, search_text)
