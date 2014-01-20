from actionable import Actionable, WithActions, Action

@WithActions
class Item(Actionable):

    def __init__(self):
        self.modified = False
        self.field_names = []
        self.item_data = None

    def set_field(self, name, value):
        if not name in self.field_names:
            self.field_names.append(name)
        setattr(self, name, value)
        if not self.modified:
            self.modified = True

    @Action("get", "reader")
    def get(self, worker):
        result = self.item_data
        result["name"] = self.name
        result["created_at"] = self.created_at.isoformat()
        result["saved_at"] = self.saved_at.isoformat()
        return result

    @Action("post", "editor", name="")
    def create_item_default_type(self, worker, name):
        return self.create_item(worker, name, "item")

    @Action("post", "editor", name="", type="")
    def create_item(self, worker, name, type):
        new_item_handle = worker.create(name, type)
        return worker.execute(new_item_handle.path, "get")
