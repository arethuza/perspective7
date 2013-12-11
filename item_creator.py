import dbgateway

class ItemCreator():

    def __init__(self, locator):
        self.locator = locator

    def create(self, parent_handle, name, type_item, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)



