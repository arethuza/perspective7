from items.item import Item
from actionable import WithActions, Action

@WithActions
class FolderItem(Item):

    @Action("get", "reader")
    def get(self, worker):
        result = self.item_data
        result["name"] = self.name
        result["created_at"] = self.created_at.isoformat()
        result["saved_at"] = self.saved_at.isoformat()
        result["children"] = worker.list_children()
        return result
