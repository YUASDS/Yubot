import yaml
import json

from pathlib import Path
from loguru import logger


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


CONFIG_PATH = Path("./config")

if (
    not CONFIG_PATH.joinpath("config.yaml").exists()
    and CONFIG_PATH.joinpath("config.exp.yaml").exists()
):
    logger.error("请修改 config.exp.yaml 并重命名为 config.yaml ！")
    logger.error("请修改 config.exp.yaml 并重命名为 config.yaml ！")
    logger.error("请修改 config.exp.yaml 并重命名为 config.yaml ！")
    exit()
elif (
    not CONFIG_PATH.joinpath("config.yaml").exists()
    and not CONFIG_PATH.joinpath("config.exp.yaml").exists()
):
    logger.error("在？宁的配置文件呢?¿?¿")
    exit()
else:
    with CONFIG_PATH.joinpath("config.yaml").open("r", encoding="utf-8") as f:
        file_data = f.read()
    yaml_data = yaml.load(file_data, Loader=yaml.FullLoader)


if CONFIG_PATH.joinpath("groupdata.json").exists():
    with CONFIG_PATH.joinpath("groupdata.json").open("r", encoding="utf-8") as f:
        group_data = json.load(f)
else:
    with CONFIG_PATH.joinpath("groupdata.json").open("w", encoding="utf-8") as f:
        group_data = {}
        json.dump(group_data, f, indent=2)


if CONFIG_PATH.joinpath("grouplist.json").exists():
    with CONFIG_PATH.joinpath("grouplist.json").open("r", encoding="utf-8") as f:
        group_list = json.load(f)
else:
    with CONFIG_PATH.joinpath("grouplist.json").open("w", encoding="utf-8") as f:
        group_list = {"white": []}
        json.dump(group_list, f, indent=2)


if CONFIG_PATH.joinpath("userlist.json").exists():
    with CONFIG_PATH.joinpath("userlist.json").open("r", encoding="utf-8") as f:
        user_list = json.load(f)
else:
    with CONFIG_PATH.joinpath("userlist.json").open("w", encoding="utf-8") as f:
        user_list = {"black": []}
        json.dump(user_list, f, indent=2)


user_black_list = user_list["black"]

if not bool(yaml_data["Final"]):
    logger.error("配置文件未修改完成，请手动编辑 config.exp.ymal 进行修改并重命名为 config.yaml")
    exit()

if (
    yaml_data["Basic"]["Permission"]["Master"]
    not in yaml_data["Basic"]["Permission"]["Admin"]
):
    yaml_data["Basic"]["Permission"]["Admin"].append(
        yaml_data["Basic"]["Permission"]["Master"]
    )
    with CONFIG_PATH.joinpath("config.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True)
    logger.warning("管理员内未包含主人，已自动添加")


def save_config():
    logger.info("正在保存配置文件")
    with CONFIG_PATH.joinpath("config.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True, Dumper=NoAliasDumper)
    with CONFIG_PATH.joinpath("groupdata.json").open("w", encoding="utf-8") as f:
        json.dump(group_data, f, indent=2, ensure_ascii=False)
    with CONFIG_PATH.joinpath("grouplist.json").open("w", encoding="utf-8") as f:
        json.dump(group_list, f, indent=2, ensure_ascii=False)
    with CONFIG_PATH.joinpath("userlist.json").open("w", encoding="utf-8") as f:
        json.dump(user_list, f, indent=2, ensure_ascii=False)


COIN_NAME = yaml_data["Basic"]["CoinName"]
save_config()
