from pathlib import Path

from tclogger import OSEnver

configs_root = Path(__file__).parents[1] / "configs"
envs_path = configs_root / "envs.json"

ENVS_ENVER = OSEnver(envs_path)
PROXY_APP_ENVS = ENVS_ENVER["proxy_app"]
PROXY_VIEW_APP_ENVS = ENVS_ENVER["proxy_view_app"]
WORKER_APP_ENVS = ENVS_ENVER["worker_app"]
VIDEO_PAGE_API_MOCKER_ENVS = ENVS_ENVER["video_page_api_mocker"]
LOG_ENVS = ENVS_ENVER["logs"]
BILI_DATA_ENVS = ENVS_ENVER["bili_data"]
BILI_DATA_ROOT = Path(BILI_DATA_ENVS["root"])

secrets_path = configs_root / "secrets.json"
SECRETS = OSEnver(secrets_path)
SQL_ENVS = SECRETS["sql"]

COOKIES_DICT = SECRETS["cookies"]
COOKIES = "; ".join(f"{key}={val}" for key, val in SECRETS["cookies"].items())
