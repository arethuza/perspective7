from items.item import Item
from actionable import WithActions, Action
from worker import ServiceException
import bcrypt
import performance as perf

PASSWORD_HASH_KEY="password_hash"

@WithActions
class UserItem(Item):
    @Action("post", "editor", password="")
    def post_set_password(self, worker, password):
        private_data = worker.get_private()
        start = perf.start()
        salt = bcrypt.gensalt(2)
        password_hash = "bcrypt:" + bcrypt.hashpw(password, salt)
        private_data[PASSWORD_HASH_KEY] = password_hash
        worker.set_private(private_data)
        perf.end(__name__, start)
        return {}

    @Action("put", "reader", password="")
    def put_login(self, worker, password):
        start = perf.start()
        private_data = worker.get_private()
        if PASSWORD_HASH_KEY in private_data:
            password_hash = private_data[PASSWORD_HASH_KEY]
            stored_hash = password_hash.split(":")[1]
            supplied_hash = bcrypt.hashpw(password, stored_hash)
            if supplied_hash == stored_hash:
                token, expires_at = worker.create_security_token()
                perf.end(__name__, start)
                return {"user_path": self.handle.path, "token": token, "expires_at": expires_at}
        perf.end(__name__, start)
        raise ServiceException(403, "Bad password")




