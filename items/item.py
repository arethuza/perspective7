from actionable import Actionable, WithActions, Action
from worker import ServiceException

@WithActions
class Item(Actionable):

    def __init__(self):
        self.modified = False
        self.modified_field_names = []
        self.item_data = None
        self.deletable = False

    def set_field(self, name, value):
        if not name in self.modified_field_names:
            self.modified_field_names.append(name)
        setattr(self, name, value)
        if not self.modified:
            self.modified = True

    @Action("init", "system")
    def init(self, worker):
        pass

    @Action("get", "reader")
    def get(self, worker):
        result = self.item_data
        result["name"] = self.name
        result["created_at"] = self.created_at.isoformat()
        result["saved_at"] = self.saved_at.isoformat()
        return result

    @Action("get", "reader", view="meta")
    def get_meta(self, worker):
        return self.get(worker)

    @Action("post", "editor", name="")
    def create_item_default_type(self, worker, name):
        return self.create_item(worker, name, "item")

    @Action("post", "editor", name="", type="")
    def create_item(self, worker, name, type):
        item_handle = worker.create(name, type)
        return worker.execute(item_handle.path, "get", view="meta")

    @Action("put", "editor", name="", _file_data="")
    def put_file(self, worker, name, _file_data):
        return self.put_file_previous(worker, name, None, _file_data)

    @Action("put", "editor", name="", previous="", _file_data="")
    def put_file_previous(self, worker, name, previous, _file_data):
        item_handle = worker.find_or_create(name, "file")
        return worker.execute(item_handle.path, "put", previous=previous, _file_data=_file_data)

    @Action("put", "editor", name="")
    def rename(self, worker, name):
        worker.set_name(name)

    @Action("delete", "editor")
    def delete(self, worker):
        if self.deletable:
            worker.delete_item()
            return {}
        else:
            raise ServiceException(403, "Item cannot be deleted")

    @Action("post", "editor", name="", password="")
    def put_login_user(self, worker, name, password):
        account_handle = worker.get_account()
        return worker.execute(account_handle.path, "post", name=name, password=password)
