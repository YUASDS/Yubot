import ujson
from pathlib import Path


def load_config(path) -> dict[str, dict[str, str]]:
    try:
        with open(path, "r", encoding="utf8") as f:
            return ujson.load(f)
    except Exception:
        return {}


trans_dict = {"friend": {}, "group": {}}

path = Path(__file__).parent / "naconfig.json"
ai_config = load_config(path)
for key in ai_config:
    trans_dict["group"][key] = ai_config[key]["token"]

# 将改变后的数据写回到源文件
with open(path, "w", encoding="utf8") as f:
    ujson.dump(trans_dict, f, ensure_ascii=False, indent=2)
print(trans_dict)
