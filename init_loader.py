import json

def load_json_with_comments(path):
    json_text = ""
    with open(path) as f:
        for line in f.readlines():
            line = line.lstrip()
            if line.startswith("#"):
                continue
            json_text += line
    return json.loads(json_text)





