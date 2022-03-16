import time
import datetime


class TimeRecorder:
    def __init__(self):
        self.time = time.time()

    def _rec(self):
        return int((time.time() - self.time) * 1000)

    def total(self):
        return calc_time_total(self._rec())


def calc_time_total(t):
    if t < 5000:
        return f"{t}毫秒"

    timedelta = datetime.timedelta(seconds=int(t / 1000))
    day = timedelta.days
    hour, mint, sec = tuple(int(n) for n in str(timedelta).split(",")[-1].split(":"))

    total = ""
    if day:
        total += "%d天" % day
    if hour:
        total += "%d小时" % hour
    if mint:
        total += "%d分钟" % mint
    if sec and not day and not hour:
        total += "%d秒" % sec

    return total
