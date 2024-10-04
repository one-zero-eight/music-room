import os
from pathlib import Path
import uvicorn

# Change dir to project root (three levels up from this file)
os.chdir(Path(__file__).parents[2])

# from src.bot.app import main  # noqa: E402

# NOTE: No need for if __name__ == "__main__":, because this is the __main__.py module already
uvicorn.main.main(
    [
        "src.bot.webserver:app",
        "--use-colors",
        "--proxy-headers",
        "--forwarded-allow-ips=*",
        "--port=8002",
    ]
)
