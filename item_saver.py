import dbgateway
import json

class ItemSaver():

    def __init__(self, locator):
        self.locator = locator

    def save(self, item):
        item_data = {}
        for field_name in sorted(self.field_names):
            value = getattr(self, field_name)
            setattr(item_data, field_name, value)
        json_data = json.dumps(item_data, indent=True)
        dbgw = dbgateway.DbGateway(self.locator)







