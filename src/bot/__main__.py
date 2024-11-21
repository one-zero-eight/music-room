import asyncio
import os

import uvicorn

from src.prepare import (
    BASE_DIR,
    check_and_prompt_bot_token,
    ensure_pre_commit_hooks,
    ensure_settings_file,
)

os.chdir(BASE_DIR)

ensure_settings_file()
ensure_pre_commit_hooks()
check_and_prompt_bot_token(use_bot_settings=True)

from src.bot.app import main  # noqa: E402
from src.bot.webserver import app  # noqa: E402


# NOTE: No need for if __name__ == "__main__":, because this is the __main__.py module already
async def start_webserver() -> None:
    config = uvicorn.Config(
        app, host="0.0.0.0", port=8002, use_colors=True, proxy_headers=True, forwarded_allow_ips="*"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_bot() -> None:
    await asyncio.gather(main(), start_webserver())


asyncio.run(run_bot())
