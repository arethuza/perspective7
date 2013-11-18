import inspect

class Actionable():

    actions = []


def action(func):
    func.is_action = True
    return func


def class_with_actions(cls):
   for name, method in inspect.getmembers(cls):
        if hasattr(method, "is_action") and method.is_action:
            cls.actions.append(method)
   return cls

