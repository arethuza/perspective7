from logging import Logger
from item_finder import ItemFinder, ItemHandle
from item_loader import ItemLoader
from item_creator import ItemCreator
from item_saver import ItemSaver
from token_manager import TokenManager
from item_deleter import ItemDeleter
from dbgateway import DbGateway
from worker import Worker, ServiceException
from init_loader import load_init_data
from file_manager import FileManager
from items.file_item import FileResponse
import performance as perf
import posixpath
import dbgateway


class Processor:

    def __init__(self):
        self.item_finder = ItemFinder()
        self.item_loader = ItemLoader()
        self.item_creator = ItemCreator()
        self.item_saver = ItemSaver()
        self.token_manager = TokenManager()
        self.file_manager = FileManager()
        self.item_deleter = ItemDeleter()

    def requires_init_data(self):
        dbgw = dbgateway.get()
        return dbgw.count_items() == 0

    def load_init_data(self):
        init_data_path = "database/init.json"
        load_init_data(init_data_path)

    def get_worker(self, item_path, user_path):
        user_handle = self.item_finder.find(user_path)
        item_handle = self.item_finder.find(item_path, user_handle)
        item = self.item_loader.load(item_handle)
        return Worker(self, item, user_handle)

    def execute(self, item_path, verb, user_handle, args):
        start = perf.start()
        if isinstance(user_handle, str):
            user_handle = self.item_finder.find(user_handle)
        item_handle = self.item_finder.find(item_path, user_handle)
        if not item_handle.exists():
            if verb == "put":
                # Supplied path doesn't exist so...
                # ... take the name from that path that was supplied
                name = posixpath.basename(item_path)
                args["name"] = name
                # ... and try use the parent item path
                item_path = posixpath.dirname(item_path)
                item_handle = self.item_finder.find(item_path, user_handle)
            else:
                raise ServiceException(404, "bad path:" + item_path)
        item = self.item_loader.load(item_handle)
        user_auth_name = item_handle.get_auth_name()
        worker = Worker(self, item, user_handle)
        item.modified = False
        result = item.invoke(verb, user_auth_name, [worker], **args)
        if item.modified:
            version = self.item_saver.save(item, user_handle)
            result["version"] = version
        perf.end(__name__, start)
        return result

    def check_login(self, item_path, verb, args):
        start = perf.start()
        if (not verb == "post") or (not "name" in args) or (not "password" in args):
            result = None
        else:
            # We are doing a "get" and supplying a name and password -> we are trying to log in
            result = self.execute(item_path, verb, self.item_finder.find_system_user(), args)
        perf.end(__name__, start)
        return result

    def get_user_for_token(self, token_value):
        user_item_id, context = self.token_manager.find_token(token_value)
        if user_item_id is None:
            raise ServiceException(403, "Invalid authentication token")
        return ItemHandle(item_id=user_item_id, path=context["path"])