from item_finder import ItemFinder, ItemHandle
from item_loader import ItemLoader
from worker import Worker

class Processor:

    def __init__(self, locator):
        self.item_finder = ItemFinder(locator)
        self.item_loader = ItemLoader(locator)

    def execute(self, item_path, verb, user_handle, args):
        if isinstance(user_handle, str):
            user_handle = self.item_finder.find(user_handle)
        item_handle = self.item_finder.find(item_path, user_handle)
        item = self.item_loader.load(item_handle)
        user_auth_name = user_handle.get_auth_name()
        worker = Worker(self, item, user_handle)
        item.modified = False
        result = item.invoke(verb, user_auth_name, [worker], **args)
        if item.modified:
            pass
        return result