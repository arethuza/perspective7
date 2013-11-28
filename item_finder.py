import dbgateway

AuthLevels = dict(system=4, admin=3, editor=2, reader=1, none=0)

def get_authorization_level(authorization):
    if not authorization in AuthLevels:
        raise Exception("Unknown auth level: {0}".format(authorization))
    return AuthLevels[authorization]

class ItemHandle:

    def __init__(self, path, item_id, auth_level, user_handle):
        self.path = path
        self.item_id = item_id
        self.auth_level = auth_level
        self.user_handle = user_handle


class ItemFinder:

    def __init__(self, locator):
        self.locator = locator

    def find(self, path, user_handle=None):
        dbgw = dbgateway.DbGateway(self.locator)
        path_parts = path.split("/")[1:]
        current_id = 1
        user_auth_level = authorize_root(user_handle)
        if path != "/":
            for part in path_parts:
                # Find the next child
                current_id, item_auth = dbgw.find_id(current_id, part, True)
                if current_id is None:
                    # Can't find a child item with that name
                    user_auth_level = AuthLevels["none"]
                    break
                if item_auth:
                    # We have found a child item, and it specifies authorization values
                    user_auth_level = self.authorize(item_auth, user_handle)
        else:
            current_id = 1
            if user_handle and user_handle.path == "/users/system":
                user_auth_level = AuthLevels["system"]
            else:
                user_auth_level = AuthLevels["reader"]
        # Always return a new ItemHandle, even if we can't find anything or we have no access
        return ItemHandle(path, current_id, user_auth_level, user_handle)

    def find_system_user(self):
        return self.find("/users/system", None)


    def authorize(self, item_auth, user_handle):
        if user_handle is None:
            return AuthLevels["reader"]
        auth_level = AuthLevels["reader"]
        for auth_id, auth_level_name in item_auth:
            if type(auth_id) is str:
                if auth_id == "everyone":
                    auth_level = AuthLevels[auth_level_name]
                else:
                    auth_user_handle = self.find(auth_id)
                    auth_id = auth_user_handle.item_id
            if user_handle.item_id == auth_id:
                auth_level = AuthLevels[auth_level_name]
                break
        return auth_level


def authorize_root(user_handle):
    if user_handle and user_handle.path == "/users/system":
        return AuthLevels["system"]
    return AuthLevels["reader"]




