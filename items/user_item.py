from items.item import Item
from actionable import WithActions, Action
import bcrypt

@WithActions
class UserItem(Item):
    @Action("post", "editor", password="")
    def post_set_password(self, worker, password):
        salt = bcrypt.gensalt(2)
        password_hash = "bcrypt:" + bcrypt.hashpw(password, salt)
        self.set_field("password_hash", password_hash)
