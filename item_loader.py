import json
import dbgateway
from items.type_item import TypeItem
from item_finder import ItemHandle, get_authorization_level

class ItemLoader:

    system_folder_id = None
    system_types_folder_id = None

    def __init__(self, locator):
        self.locator = locator

    def load(self, handle):
        if not handle.item_id:
            return None
        dbgw = dbgateway.DbGateway(self.locator)
        item_class_name, json_data = dbgw.load(handle.item_id)
        cls = get_class(item_class_name)
        new_item = cls()
        new_item.handle = handle
        item_data = json.loads(json_data)
        for name, value in item_data.items():
            setattr(new_item, name, value)
        return new_item

    def load_type(self, type_name):
        dbgw = dbgateway.DbGateway(self.locator)
        type_id, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), type_name)
        _, json_data = dbgw.load(type_id)
        type_item = TypeItem()
        type_item.handle = ItemHandle("/system/types/" + type_name, type_id, get_authorization_level("reader"), None)
        item_data = json.loads(json_data)
        for name, value in item_data.items():
            setattr(type_item, name, value)
        return type_item

    def load_template_json(self, type_name, template_name="template"):
        dbgw = dbgateway.DbGateway(self.locator)
        type_id, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), type_name)
        template_id, _ = dbgw.find_id(type_id, template_name)
        if template_id is not None:
            return dbgw.load(template_id)[1]
        # Type doesn't have its own template so use the item type template
        type_id, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), "item")
        template_id, _ = dbgw.find_id(type_id, template_name)
        if template_id is not None:
            return dbgw.load(template_id)[1]
        # Oops - no templates available
        return "{}"


    def _find_system_types_folder_id(self, dbgw):
        if ItemLoader.system_types_folder_id is None:
            ItemLoader.system_types_folder_id, _ = dbgw.find_id(self._find_system_folder_id(dbgw), "types")
        return ItemLoader.system_types_folder_id

    def _find_system_folder_id(self, dbgw):
        if ItemLoader.system_folder_id is None:
            ItemLoader.system_folder_id, _ = dbgw.find_id(1, "system")
        return ItemLoader.system_folder_id



def get_class(name):
    parts = name.split('.')
    module_name = ".".join(parts[:-1])
    m = __import__(module_name)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

