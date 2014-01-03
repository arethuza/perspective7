from items.item import Item
from actionable import WithActions, Action

@WithActions
class AccountItem(Item):
    @Action("post", "editor")
    def post_create_user(self, worker, name, password):
        users_folder_handle = worker.find_or_create("users", item_type="folder")
        worker.move("users")
        new_user_handle = worker.create(name, item_type="user")
        worker.execute(new_user_handle, "post", password=password)

