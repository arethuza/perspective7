from actionable import Actionable, WithActions, Action

@WithActions
class Item(Actionable):

    @Action("get", "reader")
    def get(self):
        pass
