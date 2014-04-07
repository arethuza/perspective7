import json
import dbgateway
from items.type_item import TypeItem
from item_finder import ItemHandle, get_authorization_level
import performance as perf

class ItemLoader:

    system_folder_id = None
    system_types_folder_id = None
    item_type_id = None

    def __init__(self, locator):
        self.locator = locator

    def load(self, handle):
        start = perf.start()
        if not handle.item_id:
            return None
        dbgw = dbgateway.DbGateway(self.locator)
        item_class_name, name, json_data, created_at, saved_at = dbgw.load(handle.item_id)
        cls = get_class(item_class_name)
        item = cls()
        item.handle = handle
        item.name = name
        item.created_at = created_at
        item.saved_at = saved_at
        item_data = json.loads(json_data)
        item.item_data = item_data
        field_names = []
        for name, value in item_data.items():
            setattr(item, name, value)
            field_names.append(name)
        item.field_names = field_names
        perf.end(__name__, start)
        return item

    def load_type(self, type_name):
        dbgw = dbgateway.DbGateway(self.locator)
        if ItemLoader.item_type_id is None:
            ItemLoader.item_type_id, _, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), "item")
        type_id, _, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), type_name)
        if type_id is None:
            return None
        _, _, json_data, _, _ = dbgw.load(type_id)
        type_item = TypeItem()
        type_item.handle = ItemHandle("/system/types/" + type_name,
                                      type_id, 0, None, get_authorization_level("reader"), None)
        if not type_item.handle.can_read():
            return None
        item_data = json.loads(json_data)
        for name, value in item_data.items():
            setattr(type_item, name, value)
        setattr(type_item, "type_path", self.find_type_path(type_item))
        return type_item

    def find_type_path(self, type_item):
        if hasattr(type_item, "base_type"):
            base_type = self.load_type(type_item["base_type"])
            return self.find_type_path(base_type) + "." + str(type_item.handle.item_id)
        else:
            return str(ItemLoader.item_type_id)

    def load_template_json(self, type_name, template_name="template"):
        dbgw = dbgateway.DbGateway(self.locator)
        type_id, _, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), type_name)
        template_id, _, _ = dbgw.find_id(type_id, template_name)
        if template_id is not None:
            return dbgw.load(template_id)[2]
        # Type doesn't have its own template so use the item type template
        type_id, _, _ = dbgw.find_id(self._find_system_types_folder_id(dbgw), "item")
        template_id, _, _ = dbgw.find_id(type_id, template_name)
        if template_id is not None:
            return dbgw.load(template_id)[2]
        # Oops - no templates available
        return "{}"


    def _find_system_types_folder_id(self, dbgw):
        if ItemLoader.system_types_folder_id is None:
            ItemLoader.system_types_folder_id, _, _ = dbgw.find_id(self._find_system_folder_id(dbgw), "types")
        return ItemLoader.system_types_folder_id

    def _find_system_folder_id(self, dbgw):
        if ItemLoader.system_folder_id is None:
            ItemLoader.system_folder_id, _, _ = dbgw.find_id(1, "system")
        return ItemLoader.system_folder_id



def get_class(name):
    parts = name.split('.')
    module_name = ".".join(parts[:-1])
    m = __import__(module_name)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

