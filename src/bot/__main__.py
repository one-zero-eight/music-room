import asyncio
import os
from pathlib import Path

import uvicorn

# Change dir to project root (three levels up from this file)
os.chdir(Path(__file__).parents[2])

from src.bot.app import main  # noqa: E402
from src.bot.webserver import app  # noqa: E402


# NOTE: No need for if __name__ == "__main__":, because this is the __main__.py module already
async def start_webserver() -> None:
    config = uvicorn.Config(app, port=8002, use_colors=True, proxy_headers=True, forwarded_allow_ips="*")
    server = uvicorn.Server(config)
    await server.serve()


async def run_bot() -> None:
    await asyncio.gather(main(), start_webserver())


asyncio.run(run_bot())
