import posixpath
from item_loader import ItemHandle, get_authorization_level

AUTH_LEVEL_NONE = get_authorization_level("none")


class ServiceException(Exception):
        def __init__(self, response_code, message):
            self.response_code = response_code
            self.message = message

class Worker():

    def __init__(self, processor, item, user_handle):
        self.processor = processor
        self.current_item = item
        self.user_handle = user_handle

    def find(self, name):
        path = posixpath.join(self.current_item.handle.path, name)
        return self.processor.item_finder.find(path, self.user_handle)

    def create(self, name, type_name):
        type_item = self.processor.item_loader.load_type(type_name)
        if type_item is None:
            raise ServiceException(403, "Unknown item type:" + type_name)
        json_data = self.processor.item_loader.load_template_json(type_name)
        self.processor.item_creator.create(self.current_item, name, type_item, json_data, self.user_handle)
        path = posixpath.join(self.current_item.handle.path, name)
        return self.processor.item_finder.find(path, self.user_handle)

    def find_or_create(self, name, type_name="item"):
        path = posixpath.join(self.current_item.handle.path, name)
        handle = self.processor.item_finder.find(path, self.user_handle)
        if not handle.item_id is None:
            return handle
        return self.create(name, type_name)

    def move(self, name):
        path = posixpath.join(self.current_item.handle.path, name)
        handle = self.processor.item_finder.find(path, self.user_handle)
        if handle.auth_level == AUTH_LEVEL_NONE:
            raise Exception("Can't move to {0}".format(path))
        self.current_item = self.processor.item_loader.load(handle)

    def execute(self, item_path, verb, **kwargs):
        return self.processor.execute(item_path, verb, self.user_handle, kwargs)

    def create_security_token(self):
        token_context = {
            "path": self.user_handle.path
        }
        return self.processor.token_manager.create_token(self.current_item.handle.item_id, 50, token_context, days=1)

    def write_file_data(self, previous_version, file_data):
        return self.processor.file_manager.write_file_data(self.current_item.handle.item_id, previous_version,
                                                           file_data, self.user_handle)
    def create_file_version(self, previous_version):
        return self.processor.file_manager.create_file_version(self.current_item.handle.item_id, previous_version,
                                                               self.user_handle)

    def list_file_blocks(self, file_version):
        return self.processor.file_manager.list_blocks(self.current_item.handle.item_id, file_version)

    def get_block_data(self, file_version, block_number):
        return self.processor.file_manager.get_block_data(self.current_item.handle.item_id, file_version, block_number)
