import inspect
from operator import attrgetter
from item_finder import get_authorization_level, get_authorization_level_name
import performance as perf
import copy

class NoAuthorizedActionException(Exception):
    pass


class Actionable():

    def invoke(self, http_method, user_auth_name, args=[], **kwargs):
        start = perf.start()
        user_auth_level = get_authorization_level(user_auth_name)
        match_found = False
        # Look at each ActionSpecification for the current class
        for action_spec in self.__class__.actions:
            # Matching HTTP method and is authorized?
            if action_spec.http_method == http_method and action_spec.auth_level <= user_auth_level:
                # Supplied number of arguments matches number of keyword parameters?
                if len(action_spec.kwargs) == len(kwargs):
                    # Not expecting any arguments?
                    if len(action_spec.kwargs) == 0:
                        match_found = True
                        break
                    else:
                        # Check the keyword parameters against supplied arguments
                        matching_count = 0
                        for name, value in action_spec.kwargs.items():
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
                                    elif argument_type == "bool":
                                        try:
                                            kwargs[name] = kwargs[name].lower() == "true"
                                        except:
                                            raise Exception("Bad bool value: {0}={1}".format(name, kwargs[name]))
                                        if expected_value:
                                            value = expected_value.lower() == "true"
                                            if kwargs[name] == value:
                                                del kwargs[name]
                                                matching_count += 1
                                        else:
                                            matching_count += 1

                        if matching_count == len(action_spec.kwargs):
                            match_found = True
                            break
        perf.end(__name__, start)
        if match_found:
            call_start = perf.start()
            result = action_spec.f(self, *args, **kwargs), action_spec.return_type
            perf.end2(self.__class__.__name__, action_spec.name, call_start)
            return result
        else:
            raise NoAuthorizedActionException()

def list_actions(cls):
    return [action_spec.get_details() for action_spec in cls.actions if not action_spec.http_method.startswith("_")]


class Action:
    def __init__(self, http_method, auth_name, **kwargs):
        self.http_method = http_method
        self.auth_level = get_authorization_level(auth_name)
        self.kwargs = kwargs

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        wrapped.action_spec = ActionSpecification(f, wrapped, self)
        return wrapped


class ActionSpecification():

    def __init__(self, f, wrapped, action):
        self.distance = 1000000
        self.f = f
        self.name = f.__name__
        _, self.line_number = inspect.getsourcelines(f)
        self.wrapped = wrapped
        self.http_method = action.http_method
        self.auth_level = action.auth_level
        self.kwargs = action.kwargs
        self.return_type = f.__annotations__["return"] if "return" in f.__annotations__ else None
        self.params = []
        for arg in self.kwargs:
            if not arg in f.__annotations__:
                continue
            doc = f.__annotations__[arg]
            self.params.append({"name": arg, "doc": doc})

    def get_details(self):
        return {
            "doc": inspect.getdoc(self.f),
            "auth_level": get_authorization_level_name(self.auth_level),
            "http_method": self.http_method,
            "params": self.params,
            "returns": self.return_type
        }


def WithActions(cls):
    cls.actions = []
    for name, method in inspect.getmembers(cls):
        if hasattr(method, "action_spec"):
            action_spec = getattr(method, "action_spec")
            defining_class = get_class_that_defined_method(cls, name)
            action_spec.distance = get_distance_from_actionable(defining_class)
            cls.actions.append(action_spec)
    cls.actions.sort(key=attrgetter("distance", "line_number"), reverse=True)
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
