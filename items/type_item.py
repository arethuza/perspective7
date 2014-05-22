from actionable import Actionable, WithActions, Action
from items.item import Item

@WithActions
class TypeItem(Item):
    pass

    @Action("get", "reader")
    def get(self, worker):
        """ List the actions for the type defined by the current item """
        class_name = self.props["item_class"]
        return worker.list_actions(class_name)