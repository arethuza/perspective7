from actionable import Actionable, WithActions, Action

@WithActions
class Item(Actionable):

    def __init__(self):
        self.modified = False
        self.field_names = []

    def set_field(self, name, value):
        if not name in self.field_names:
            self.field_names.append(name)
        setattr(self, name, value)
        if not self.modified:
            self.modified = True

    @Action("get", "reader")
    def get(self, worker):
        pass
