import dbgateway

class ItemDeleter():

    def delete_item(self, item_id):
        dbgw = dbgateway.get()
        dbgw.delete_item(item_id)
