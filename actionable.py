import inspect
from operator import itemgetter

class Actionable():

    def invoke(self, verb, user_auth, **kwargs):
        match_found = False
        for _, _, f, action_verb, action_auth, action_args in self.__class__.actions:
            if action_verb == verb:
                if len(action_args) == 0 and len(kwargs) == 0:
                    match_found = True
                else:
                    for name, value in action_args.items():
                        if name in kwargs and kwargs[name] == value:
                            # We know the value of parameter 'name', so don't bother passing it into f
                            del kwargs[name]
                            match_found = True
                            break
            if match_found:
                return f(self, **kwargs)



class Action:
    def __init__(self, verb, authorization, **kwargs):
        self.verb = verb
        self.authorization = authorization
        self.args = kwargs
    def __call__(self, f):
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        _, line_number = inspect.getsourcelines(f)
        wrapped.action_spec = [1000000, line_number, wrapped, self.verb, self.authorization, self.args]
        return wrapped


def WithActions(cls):
    cls.actions = []
    members = inspect.getmembers(cls)
    for name, method in members:
        if hasattr(method, "action_spec"):
            action_spec = getattr(method, "action_spec")
            defining_class = get_class_that_defined_method(cls, name)
            action_spec[0] = distance_from_actionable(defining_class)
            cls.actions.append(action_spec)
    cls.actions.sort(key=itemgetter(0, 1), reverse=True)
    return cls

def distance_from_actionable(cls):
    classes = inspect.getmro(cls)
    result = 0
    for c in classes:
        if c == object:
            return -1
        elif c == Actionable:
            return result
        else:
            result += 1

def get_class_that_defined_method(cls, name):
    classes = list(inspect.getmro(cls))
    classes.reverse()
    for c in classes:
        for member_name, member in inspect.getmembers(c):
            if member_name == name:
                return c
    return None

