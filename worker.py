import posixpath
from item_loader import ItemHandle, get_authorization_level

AUTH_LEVEL_NONE = get_authorization_level("none")

class Worker():

    def __init__(self, processor, item, user_handle):
        self.processor = processor
        self.current_item = item
        self.user_handle = user_handle

    def find(self, path):
        return self.processor.item_finder.find(path, self.user_handle)

    def create(self, name, type_name):
        type_item = self.processor.item_loader.load_type(type_name)
        json_data = self.processor.item_loader.load_template_json(type_name)
        self.processor.item_creator.create(self.current_item, name, type_item, json_data, self.user_handle)
        path = posixpath.join(self.current_item.handle.path, name)
        return self.processor.item_finder.find(path, self.user_handle)

    def find_or_create(self, name, type_name):
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


    def execute(self, verb, **kwargs):
        pass