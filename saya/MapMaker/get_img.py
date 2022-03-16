import os


def path(config_path):
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf8") as f:
            f.write("{}")
