from items.folder_item import FolderItem
from actionable import WithActions, Action
from worker import ServiceException
import performance as perf

@WithActions
class AccountItem(FolderItem):

    @Action("post", "editor", new_name="", new_password="")
    def post_create_user(self, worker, new_name, new_password):
        users_folder_handle = worker.find_or_create("users", type_name="folder")
        worker.move("users")
        new_user_handle = worker.create(new_name, "user")
        return worker.execute(new_user_handle.path, "post", password=new_password)

    @Action("post", "editor", name="", password="")
    def post_login_user(self, worker, name, password):
        worker.move("users")
        user_handle = worker.find(name)
        if not user_handle.can_read():
            raise ServiceException(404, "Unknown user:{0}".format(name))
        response = worker.execute(user_handle.path, "put", password=password)
        response["account_path"] = self.handle.path
        return response

    @Action("get", "system", performance="true")
    def get_performance(self, worker):
        return perf.get_report()



