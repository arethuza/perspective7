import dbgateway
import json


class ItemSaver():

    def save(self, item, user_handle):
        json_data = json.dumps(item.props)
        dbgw = dbgateway.get()
        dbgw.save_item_version(item.handle.item_id)
        return dbgw.update_item(item.handle.item_id, json_data, user_handle.item_id)

    def set_private(self, item_handle, data, user_handle):
        dbgw = dbgateway.get()
        return dbgw.update_private(item_handle.item_id, json.dumps(data), user_handle.item_id)

    def set_item_name(self, item_handle, name):
        dbgw = dbgateway.get()
        dbgw.set_item_name(item_handle.item_id, name)





