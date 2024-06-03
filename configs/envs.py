from pathlib import Path

from tclogger import OSEnver

configs_root = Path(__file__).parents[1] / "configs"
envs_path = configs_root / "envs.json"

ENVS_ENVER = OSEnver(envs_path)
PROXY_APP_ENVS = ENVS_ENVER["proxy_app"]
WORKER_APP_ENVS = ENVS_ENVER["worker_app"]
VIDEO_PAGE_API_MOCKER_ENVS = ENVS_ENVER["video_page_api_mocker"]
LOG_ENVS = ENVS_ENVER["logs"]

secrets_path = configs_root / "secrets.json"
SECRETS = OSEnver(secrets_path)
SQL_ENVS = SECRETS["sql"]

COOKIES = "; ".join(f"{key}={val}" for key, val in SECRETS["cookies"].items())
