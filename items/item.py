from actionable import Actionable, WithActions, Action

@WithActions
class Item(Actionable):

    def __init__(self):
        self.name = None
        self.type_name = None
        self.deletable = False
        self.props = None
        self.created_at = None
        self.created_by_path = None
        self.saved_at = None
        self.saved_by_path = None
        self.props = None

    @Action("_init", "system")
    def init(self, worker):
        pass

    @Action("get", "reader")
    def get(self, worker):
        return {
            "name": self.name,
            "type": self.type_name,
            "props": self.props,
            "created_at": self.created_at.isoformat(),
            "created_by_path": self.created_by_path,
            "saved_by_path": self.created_by_path,
            "saved_at": self.created_at.isoformat(),
        }

    @Action("get", "reader", view="meta")
    def get_meta(self, worker):
        return self.get(worker)

    @Action("post", "editor", name="")
    def create_item_default_type(self, worker,
                                 name: "string: name of item to be created"):
        return self.create_item(worker, name, "item")

    @Action("post", "editor", name="", type="")
    def create_item(self, worker,
                    name: "string: name of item to be created",
                    type: "string: name of type of item to be created") -> "get-item":
        """Create child item with the specified name and type"""
        item_handle = worker.create(name, type)
        response, _ = worker.execute(item_handle.path, "get", view="meta")
        return response

    @Action("put", "editor", name="", _file_data="")
    def put_file(self, worker,
                 name: "Name for the new file",
                 _file_data: "File data"):
        """Put a file"""
        return self.put_file_previous(worker, name, None, _file_data)

    @Action("put", "editor", name="", previous="", _file_data="")
    def put_file_previous(self, worker,
                          name: "string: Name for the new file",
                          previous: "integer: Previous version",
                          _file_data) -> "get-file":
        """Put a file specifying a previous version"""
        item_handle = worker.find_or_create(name, "file")
        response, _ = worker.execute(item_handle.path, "put", previous=previous, _file_data=_file_data)
        return response

    @Action("put", "editor", name="")
    def rename(self, worker,
               name: "string: New name for the current item") -> "":
        """Rename the current item"""
        worker.set_name(name)
        return {}

    @Action("delete", "editor")
    def delete(self, worker) -> "":
        """Delete the current item"""
        worker.delete_item()
        return {}

    @Action("post", "editor", name="", password="")
    def put_login_user(self, worker,
                       name: "string: User name",
                       password: "string: User password") -> "post-login":
        """Log in using the supplied user name and password to the nearest parent account item"""
        account_handle = worker.get_account()
        response, _ = worker.execute(account_handle.path, "post", name=name, password=password)
        return response
