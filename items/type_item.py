from actionable import Actionable, WithActions, Action
from items.item import Item

@WithActions
class TypeItem(Item):
    pass

    @Action("get", "reader")
    def get(self, worker):
        return self.list_actions()