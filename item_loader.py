import json
import dbgateway


class ItemLoader:

    def __init__(self, locator):
        self.locator = locator

    def load(self, handle):
        if not handle.item_id:
            return None
        dbgw = dbgateway.DbGateway(self.locator)
        item_class_name, json_data = dbgw.load(handle.item_id)
        cls = get_class(item_class_name)
        new_item = cls()
        item_data = json.loads(json_data)
        for name, value in item_data.items():
            setattr(new_item, name, value)
        return  new_item


def get_class(name):
    parts = name.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m