import json
import os
import dbgateway

def load_json_with_comments(path):
    json_text = ""
    with open(path) as f:
        for line in f.readlines():
            line = line.lstrip()
            if line.startswith("#"):
                continue
            json_text += line
    return json.loads(json_text)


def load_init_data(path, locator):
    init_data = load_json_with_comments(path)
    dbgw = dbgateway.DbGateway(locator)
    types_to_resolve = []
    for data in init_data:
        item_path = data["path"]
        item_data = data["data"] if "data" in data else {}
        item_type = data["type"]
        if item_path == "/":
            parent_id = None
            item_name = ""
            parent_id_path = ""
        else:
            parent_path = os.path.dirname(item_path)
            parent_id, parent_id_path = find_item_id(dbgw, parent_path)
            item_name = os.path.basename(item_path)
        search_text = item_name
        if "title" in item_data:
            search_text += " " + item_data["title"]
        dbgw.create_item_initial(parent_id, item_name, parent_id_path, json.dumps(item_data), search_text)
        types_to_resolve.append((item_path, item_type))
    type_type_id, _ = find_item_id(dbgw, "/system/types/type")
    system_user_id, _ = find_item_id(dbgw, "/users/system")
    for item_path,item_type in types_to_resolve:
        type_path = "/system/types/" + item_type
        type_id, _ = find_item_id(dbgw, type_path)
        item_id, _ = find_item_id(dbgw, item_path)
        # FIXME - calculate type_id_path in general way
        type_id_path = "{0}.{1}".format(type_type_id, type_id)
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



