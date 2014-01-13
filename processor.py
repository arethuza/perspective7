from item_finder import ItemFinder, ItemHandle
from item_loader import ItemLoader
from item_creator import ItemCreator
from item_saver import ItemSaver
from token_manager import TokenManager
from worker import Worker, ServiceException

class Processor:

    def __init__(self, locator):
        self.item_finder = ItemFinder(locator)
        self.item_loader = ItemLoader(locator)
        self.item_creator = ItemCreator(locator)
        self.item_saver = ItemSaver(locator)
        self.token_manager = TokenManager(locator)

    def get_worker(self, item_path, user_path):
        user_handle = self.item_finder.find(user_path)
        item_handle = self.item_finder.find(item_path, user_handle)
        item = self.item_loader.load(item_handle)
        return Worker(self, item, user_handle)

    def execute(self, item_path, verb, user_handle, args):
        if isinstance(user_handle, str):
            user_handle = self.item_finder.find(user_handle)
        item_handle = self.item_finder.find(item_path, user_handle)
        item = self.item_loader.load(item_handle)
        user_auth_name = item_handle.get_auth_name()
        worker = Worker(self, item, user_handle)
        item.modified = False
        result = item.invoke(verb, user_auth_name, [worker], **args)
        if item.modified:
            self.item_saver.save(item, user_handle)
        return result

    def check_login(self, item_path, verb, args):
        if (not verb == "get") or (not "name" in args) or (not "password" in args):
            return None
        # We are doing a "get" and supplying a name and password -> we are trying to log in
        return self.execute(item_path, verb, self.item_finder.find_system_user(), args)

    def get_user_for_token(self, token_value):
        user_item_id = self.token_manager.find_token(token_value)
        if user_item_id is None:
            raise ServiceException(403, "Invalid authentication token")
        return ItemHandle(item_id=user_item_id)


