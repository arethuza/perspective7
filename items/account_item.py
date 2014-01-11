from items.item import Item
from actionable import WithActions, Action

@WithActions
class AccountItem(Item):
    @Action("post", "editor", name="", password="")
    def post_create_user(self, worker, name, password):
        users_folder_handle = worker.find_or_create("users", type_name="folder")
        worker.move("users")
        new_user_handle = worker.create(name, "user")
        worker.execute(new_user_handle.path, "post", password=password)

    @Action("post", "editor", name="", password="")
    def get_login_user(self, worker, name, password):
        worker.move("users")
        user_handle = worker.find(name)
        worker.execute(user_handle.path, "get", password=password)


