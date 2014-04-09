import dbgateway
import performance as perf

AuthLevelNames = ["none", "reader", "editor", "admin", "system"]
AuthLevels = {}
for level in range(0, len(AuthLevelNames)):
    AuthLevels[AuthLevelNames[level]] = level


def get_authorization_level(authorization):
    if not authorization in AuthLevels:
        raise Exception("Unknown auth level: {0}".format(authorization))
    return AuthLevels[authorization]

class ItemHandle:

    def __init__(self, path=None, item_id=None, version=None, id_path=None, auth_level=None, user_handle=None):
        self.path = path
        self.version = version
        self.item_id = item_id
        self.id_path = id_path
        self.auth_level = auth_level
        self.user_handle = user_handle

    def get_auth_name(self):
        return AuthLevelNames[self.auth_level]

    def can_read(self):
        return self.auth_level > 0

    def exists(self):
        return self.item_id is not None


class ItemFinder:

    def __init__(self, locator):
        self.locator = locator

    def find(self, path, user_handle=None):
        start = perf.start()
        dbgw = dbgateway.get_from_thread()
        path_parts = path.split("/")[1:]
        current_id = 1
        user_auth_level = authorize_root(user_handle)
        id_path = str(current_id)
        version = -1
        if path != "/":
            if len(path_parts) == 0:
                current_id = None
                id_path = None
                user_auth_level = AuthLevels["none"]
            else:
                for part in path_parts:
                    # Find the next child
                    current_id, item_auth, version = dbgw.find_id(current_id, part, True)
                    if current_id is None:
                        # Can't find a child item with that name
                        user_auth_level = AuthLevels["none"]
                        break
                    elif user_handle and current_id == user_handle.item_id:
                        # users can always edit themselves
                        user_auth_level = AuthLevels["editor"]
                    elif item_auth:
                        # We have found a child item, and it specifies authorization values
                        user_auth_level = self.authorize(item_auth, user_handle)
                    id_path += "." + str(current_id)
        else:
            current_id = 1
            if user_handle and user_handle.path == "/users/system":
                user_auth_level = AuthLevels["system"]
            else:
                user_auth_level = AuthLevels["reader"]
        # Always return a new ItemHandle, even if we can't find anything or we have no access
        result = ItemHandle(path, current_id, version, id_path, user_auth_level, user_handle)
        perf.end(__name__, start)
        return result

    def find_system_user(self):
        return self.find("/users/system", None)

    def authorize(self, item_auth, user_handle):
        start = perf.start()
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
        perf.end(__name__, start)
        return auth_level

    def get_path(self, item_id):
        dbgw = dbgateway.get_from_thread()
        id_path = dbgw.get_item_id_path(item_id)
        return "/".join([dbgw.get_item_name(int(id)) for id in id_path.split(".")])

def authorize_root(user_handle):
    if user_handle and user_handle.path == "/users/system":
        return AuthLevels["system"]
    return AuthLevels["reader"]




