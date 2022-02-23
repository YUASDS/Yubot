import numpy as np
import matplotlib.pyplot as plt

from io import BytesIO
from pathlib import Path
from scipy import interpolate
from matplotlib.font_manager import FontProperties

font = Path().joinpath("font", "sarasa-mono-sc-regular.ttf")
zhfont1 = FontProperties(fname=font)


async def get_mapping(talk_num, time):

    x_range = range(1, 25, 1)
    x = np.array(x_range)
    y = np.array(talk_num)

    x_new = np.linspace(x.min(), x.max(), 600)
    # y_new = np.linspace(y.min(), y.max(), 600)
    y_new = interpolate.splev(x_new, interpolate.splrep(x, y))

    plt.figure(dpi=96, figsize=(18, 7))
    plt.plot(x_new, y_new, c="violet", linewidth=3)
    plt.fill_between(x_new, y_new, 0, facecolor="violet", alpha=0.5)
    plt.scatter(x, y, c="violet", linewidths=2)
    plt.scatter(x, y, c="white", s=6).set_zorder(10)
    plt.xticks(x_range, labels=time)

    for a, b in zip(x, y):
        plt.text(a, b + 5, "%.0f" % b, ha="center", va="bottom", fontsize=12)

    plt.title("信息量统计", fontsize=24, fontproperties=zhfont1)
    plt.tick_params(axis="both", labelsize=12)

    bio = BytesIO()
    plt.savefig(bio, bbox_inches="tight", format="jpeg")
    return bio.getvalue()
