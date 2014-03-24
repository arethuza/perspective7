from items.item import Item
from actionable import WithActions, Action
from worker import ServiceException
import bcrypt

@WithActions
class UserItem(Item):
    @Action("post", "editor", password="")
    def post_set_password(self, worker, password):
        salt = bcrypt.gensalt(2)
        password_hash = "bcrypt:" + bcrypt.hashpw(password, salt)
        self.set_field("password_hash", password_hash)
        return {}

    @Action("get", "reader", password="")
    def get_login(self, worker, password):
        stored_hash = self.password_hash.split(":")[1]
        supplied_hash = bcrypt.hashpw(password, stored_hash)
        if supplied_hash == stored_hash:
            token, expires_at = worker.create_security_token()
            return {"user_path": self.handle.path, "token": token, "expires_at": expires_at}
        else:
            raise ServiceException(403, "Invalid password")




