import ujson
import os

config_path = os.path.join(os.path.dirname(__file__), "naconfig.json")


def save_config(config: dict, path):
    try:
        with open(path, "w", encoding="utf8") as f:
            ujson.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False


def load_config(path)->dict[str, dict[str, str]]:
    try:
        with open(path, "r", encoding="utf8") as f:
            return ujson.load(f)
    except Exception:
        return {}


if not os.path.exists(config_path):
    with open(config_path, "w", encoding="utf8") as f:
        f.write('{"friend":{},"group":{}}')
ai_config = load_config(config_path)

def get_key(type, id:int):
    return ai_config[type].get(str(id), None)

def set_key(type,id,key):
    ai_config[type][str(id)] = key
    save_config(ai_config, config_path)
    