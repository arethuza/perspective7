import dbgateway
import json


class ItemSaver():

    def __init__(self, locator):
        self.locator = locator

    def save(self, item, user_handle):
        item_data = {}
        for field_name in sorted(item.field_names):
            value = getattr(item, field_name)
            item_data[field_name] = value
        json_data = json.dumps(item_data)
        dbgw = dbgateway.DbGateway(self.locator)
        dbgw.save_item_version(item.handle.item_id)
        return dbgw.update_item(item.handle.item_id, json_data, user_handle.item_id)







