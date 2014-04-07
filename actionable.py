import inspect
from operator import itemgetter
from item_finder import get_authorization_level
import performance as perf

class NoAuthorizedActionException(Exception):
    pass


class Actionable():

    def invoke(self, verb, user_auth_name, args=[], **kwargs):
        start = perf.start()
        user_auth_level = get_authorization_level(user_auth_name)
        match_found = False
        function_name = None
        for _, name, _, f, action_verb, action_auth_level, action_kwargs in self.__class__.actions:
            if action_verb == verb and action_auth_level <= user_auth_level:
                if len(action_kwargs) == len(kwargs):
                    if len(action_kwargs) == 0:
                        function_name = name
                        match_found = True
                        break
                    else:
                        matching_count = 0
                        for name, value in action_kwargs.items():
                            if name in kwargs and value == "":
                                # Allow any value, pass value in
                                matching_count += 1
                            elif name in kwargs:
                                if kwargs[name] == value:
                                    # We know the value of parameter 'name', so don't bother passing it into f
                                    del kwargs[name]
                                    matching_count += 1
                                elif ":" in value:
                                    # We have a type and possibly value specified
                                    type_value = value.split(":")
                                    if len(type_value) != 2:
                                        raise Exception("Invalid action argument spec: " + value)
                                    argument_type, expected_value = type_value
                                    if argument_type == "int":
                                        try:
                                            kwargs[name] = int(kwargs[name])
                                        except:
                                            raise Exception("Bad int value: {0}={1}".format(name, kwargs[name]))
                                        if expected_value:
                                            value = int(expected_value)
                                            if kwargs[name] == value:
                                                del kwargs[name]
                                                matching_count += 1
                                        else:
                                            matching_count += 1
                        if matching_count == len(action_kwargs):
                            function_name = name
                            match_found = True
                            break
        perf.end(__name__, start)
        if match_found:
            call_start = perf.start()
            result = f(self, *args, **kwargs)
            perf.end2(self.__class__.__name__, function_name, call_start)
            return result
        else:
            raise NoAuthorizedActionException()


class Action:
    def __init__(self, verb, auth_name, **kwargs):
        self.verb = verb
        self.auth_level = get_authorization_level(auth_name)
        self.kwargs = kwargs
    def __call__(self, f):
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        _, line_number = inspect.getsourcelines(f)
        wrapped.action_spec = [1000000, f.__name__, line_number, wrapped, self.verb, self.auth_level, self.kwargs]
        return wrapped

def WithActions(cls):
    cls.actions = []
    for name, method in inspect.getmembers(cls):
        if hasattr(method, "action_spec"):
            action_spec = getattr(method, "action_spec")
            defining_class = get_class_that_defined_method(cls, name)
            action_spec[0] = get_distance_from_actionable(defining_class)
            cls.actions.append(action_spec)
    cls.actions.sort(key=itemgetter(0, 1), reverse=True)
    return cls


def get_distance_from_actionable(cls):
    result = 0
    for c in inspect.getmro(cls):
        if c == object:
            return -1
        elif c == Actionable:
            return result
        else:
            result += 1


def get_class_that_defined_method(cls, name):
    for c in reversed(inspect.getmro(cls)):
        for member_name, member in inspect.getmembers(c):
            if member_name == name:
                return c
    return None
