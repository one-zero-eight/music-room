import os
import sys

from src.prepare import (
    BASE_DIR,
    check_and_generate_secret_api_key,
    check_and_prompt_api_jwt_token,
    check_and_prompt_bot_token,
    check_database_access,
    ensure_pre_commit_hooks,
    ensure_settings_file,
)

os.chdir(BASE_DIR)

ensure_settings_file()
ensure_pre_commit_hooks()
check_and_prompt_api_jwt_token()
check_and_prompt_bot_token(use_bot_settings=False)
check_and_generate_secret_api_key()
check_database_access()

import uvicorn  # noqa: E402

# Get arguments from command
args = sys.argv[1:]
extended_args = [
    "src.api.app:app",
    "--use-colors",
    "--proxy-headers",
    "--forwarded-allow-ips=*",
    "--port=8001",
    *args,
]

print(f"🚀 Starting Uvicorn server: 'uvicorn {' '.join(extended_args)}'")
uvicorn.main.main(extended_args)
