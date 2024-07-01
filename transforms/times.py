from datetime import datetime


def get_now_ts_str() -> tuple[int, str]:
    now = datetime.now()
    now_ts = round(now.timestamp())
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return now_ts, now_str


if __name__ == "__main__":
    now_ts, now_str = get_now_ts_str()
    print(now_ts, now_str)

    # python -m transforms.times
