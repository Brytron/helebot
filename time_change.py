from datetime import datetime, timedelta
from threading import Timer
import Sqlite

def initialize_daily(set_time = "10:00"):

    time_split = set_time.split(":")
    today=datetime.today()
    print(today)
    post_on = today.replace(day=today.day, hour=int(time_split[0]), minute=int(time_split[1]), second=0, microsecond=0)\

    if post_on < today:
        post_on = post_on + timedelta(days=1)

    print(post_on)
    delta_t=post_on-today
    print(delta_t)

    return delta_t.total_seconds()