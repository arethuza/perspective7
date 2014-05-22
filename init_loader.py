import json
import os
import dbgateway
import inspect

from item_loader import get_class


def load_json_with_comments(path):
    json_text = ""
    with open(path) as f:
        for line in f.readlines():
            line = line.lstrip()
            if line.startswith("#"):
                continue
            json_text += line
    return json.loads(json_text)


def load_init_data(path):
    init_data = load_json_with_comments(path)
    dbgw = dbgateway.get()
    types_to_resolve = []
    type_names_to_class_names = {}
    for data in init_data:
        item_path = data["path"]
        item_props = data["props"] if "props" in data else {}
        item_auth = data["auth"] if "auth" in data else {}
        item_type = data["type"]
        item_title = data["title"] if "title" in data else {}
        item_name = os.path.basename(item_path)
        if item_path == "/":
            parent_id = None
            item_name = ""
            parent_id_path = ""
        else:
            parent_path = os.path.dirname(item_path)
            parent_id, parent_id_path = find_item_id(dbgw, parent_path)
        search_text = item_name
        if item_title:
            search_text += " " + item_title
        item_data = {
            "auth": item_auth,
            "props": item_props,
            "saved_by_path": "/users/system",
            "created_by_path": "/users/system",
            "title": item_title
        }
        dbgw.create_item_initial(parent_id, item_name, parent_id_path, json.dumps(item_data), search_text)
        types_to_resolve.append((item_path, item_type))
        if item_type == "type":
            class_name = item_props["item_class"]
            type_names_to_class_names[item_name] = class_name
    type_type_id, _ = find_item_id(dbgw, "/system/types/type")
    system_user_id, _ = find_item_id(dbgw, "/users/system")
    for item_path,item_type in types_to_resolve:
        type_path = "/system/types/" + item_type
        type_id, _ = find_item_id(dbgw, type_path)
        item_id, _ = find_item_id(dbgw, item_path)
        if item_type in type_names_to_class_names:
            item_class = type_names_to_class_names[item_type]
        else:
            item_data = json.loads(dbgw.load(type_id)[2])
            item_class = item_data["props"]["item_class"]
        type_id_path = find_type_path(dbgw, item_class)
        dbgw.set_item_type_user(item_id, type_id, type_id_path, system_user_id)

def find_item_id(dbgw, path):
    if path == "/":
        return 1, "1"
    current_id = 1
    current_id_path = None
    path_parts = path.split("/")[1:]
    for part in path_parts:
        current_id, current_id_path, _ = dbgw.find_id(current_id, part)
        if current_id is None:
            break
    return current_id, current_id_path

def find_type_path(dbgw, class_name):
    cls = get_class(class_name)
    base_classes = inspect.getmro(cls)
    type_ids = []
    for cls in base_classes:
        type_name = cls.__name__[:-4].lower()
        type_name = type_name if len(type_name) > 0 else "item"
        type_path = "/system/types/" + type_name
        type_ids.append(str(find_item_id(dbgw, type_path)[0]))
        if type_name == "item":
            break
    return ".".join(reversed(type_ids))

