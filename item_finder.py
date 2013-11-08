import dbgateway

AuthLevels = dict(root=4, admin=3, editor=2, reader=1, none=0)


class ItemHandle:

    def __init__(self, path, item_id, auth_level, user_handle):
        self.path = path
        self.item_id = item_id
        self.auth_level = auth_level
        self.user_handle = user_handle


class ItemFinder:

    def __init__(self, locator):
        self.locator = locator

    def find(self, path, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        path_parts = path.split("/")[1:]
        current_id = None
        user_auth_level = AuthLevels["reader"]
        for part in path_parts:
            current_id, item_auth = dbgw.find_id(current_id, part, False)
            if current_id is None:
                break
            if item_auth is not None:
                user_auth_level = authorize(item_auth, user_handle.item_id)
        return ItemHandle(path, current_id, user_auth_level, user_handle)


def authorize(self, item_auth, user_id):
    for auth_id, auth_level_name, auth_type in item_auth:
        if user_id == auth_id:
            return AuthLevels[auth_level_name]





