import dbgateway
from item_finder import ItemHandle

class ItemCreator():

    def __init__(self, locator):
        self.locator = locator

    def create(self, parent_item, name, type_item, json_data, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        item_id = dbgw.create_item(parent_item.handle.item_id, name, parent_item.handle.id_path,
                                   type_item.handle.item_id, type_item.type_path,
                                   json_data, user_handle.item_id, "")



