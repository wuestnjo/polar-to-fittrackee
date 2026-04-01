import json

def load_user_json(user):
    with open(f"./config/users/{user}.json") as f:
        config = json.loads(f.read())
    return config

def load_mapping_json(name):
    with open(f"./config/mapping_{name}.json") as f:
        mapping = json.loads(f.read())
    return mapping
