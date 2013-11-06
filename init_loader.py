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
    for item_data in init_data:
        item_path = item_data["path"]
        if item_path == "/":
            parent_id = None
            item_name = ""
            id_path = ""
        else:
            parent_path = os.path.dirname(item_path)
            parent_id = find_item_id(dbgw, parent_path)
            item_name = os.path.basename(item_path)
        # dbgw.create_item_initial(parent_id, item_name,


def find_item_id(dbgw, path):
    if path == "/":
        return 1, "1"
    current_id = 1
    current_id_path = None
    path_parts = path.split("/")[1:]
    length = len(path_parts)
    for part in path_parts:
        current_id, current_id_path = dbgw.find_id(current_id, part)
        if current_id is None:
            break
    return current_id, current_id_path



