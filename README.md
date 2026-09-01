# InNoHassle Music room

[![GitHub Actions pre-commit](https://img.shields.io/github/actions/workflow/status/one-zero-eight/InNoHassle-MusicRoom/pre-commit.yaml?label=pre-commit)](https://github.com/one-zero-eight/InNoHassle-MusicRoom/actions)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-MusicRoom&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-MusicRoom)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-MusicRoom&metric=bugs)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-MusicRoom)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-MusicRoom&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-MusicRoom)

## Table of contents

Did you know that GitHub supports table of
contents [by default](https://github.blog/changelog/2021-04-13-table-of-contents-support-in-markdown-files/) 🤔

## About

This is the API and Telegram bot for the Music room service in the InNoHassle ecosystem.

### Features

- 🎵 Booking Music room
- 📅 Schedule of Music room
- 🔒 Roles and permissions
- 🇷🇺 Russian (Cyrillic) full name required before creating a booking
- 🔔 Notifications (upcoming bookings, receptionist digests) orchestrated with Prefect

### Components

The repository ships two runnable apps that share the same code and `settings.yaml`:

- **API** (`src/api`) — FastAPI app served by Uvicorn on port `8001`, Swagger UI at `/docs`.
- **Bot** (`src/bot`) — Aiogram 3 long-polling bot plus a small Uvicorn webserver on port `8002`.

### Technologies

- [Python 3.13](https://www.python.org/downloads/) & [uv](https://docs.astral.sh/uv/)
- [FastAPI](https://fastapi.tiangolo.com/) & [Pydantic](https://docs.pydantic.dev/latest/)
- [Aiogram 3](https://docs.aiogram.dev/en/latest/) & [aiogram-dialog](https://aiogram-dialog.readthedocs.io/)
- [Prefect 3](https://docs.prefect.io/) for notification workflow orchestration
- Database and ORM: [PostgreSQL](https://www.postgresql.org/), [SQLAlchemy](https://www.sqlalchemy.org/),
  [asyncpg](https://magicstack.github.io/asyncpg/), [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Redis](https://redis.io/) for bot FSM storage
- Formatting and linting: [Ruff](https://docs.astral.sh/ruff/), [prek](https://prek.j178.dev/)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
  [GitHub Actions](https://github.com/features/actions)

## Development

### Set up for development

1. Install [Python 3.13](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Install project dependencies:
   ```bash
   uv sync
   ```
3. Start the API:
   ```bash
   uv run python -m src.api
   ```
   > Follow provided instructions if needed. Swagger UI: http://localhost:8001/docs
4. Start the Bot:
   ```bash
   uv run python -m src.bot
   ```
   > Follow provided instructions if needed.

> [!NOTE]
> On the first run each app goes through `src/prepare.py`, which:
> - copies `settings.example.yaml` to `settings.yaml` if it is missing;
> - installs the prek git hooks;
> - prompts for the InNoHassle Accounts JWT token and the bot token (opening the relevant page in your browser);
> - generates a random `api_settings.api_key`;
> - checks the database connection, starts the `db` container with `docker compose up -d --wait db` if it is
>   unreachable, and runs `alembic upgrade head`.

> [!NOTE]
> The bot and API schedule their notification flows through Prefect. To record runs on a real
> Prefect server instead of the ephemeral one, start it with `prefect server start` and export
> `PREFECT_API_URL=http://127.0.0.1:4200/api` before launching them. Without it, Prefect falls
> back to an ephemeral local API and the schedulers still work. The Prefect UI is available at
> http://localhost:4200 (also started as the `prefect-server` service in Docker Compose).

> [!IMPORTANT]
> For endpoints requiring authorization click "Authorize" button in Swagger UI

> [!TIP]
> Edit `settings.yaml` according to your needs, you can view the schema in
> [config_schema.py](src/config_schema.py) and in [settings.schema.yaml](settings.schema.yaml).
> Point at a different file with the `SETTINGS_PATH` environment variable.

### Database migrations

Migrations are managed with Alembic and applied automatically on the first app run. Run them manually with:

```bash
uv run alembic upgrade head            # apply latest
uv run alembic revision --autogenerate -m "message"   # create a new migration
```

### Running checks

```bash
uv run prek run --all-files   # ruff lint + format, translations, settings schema
uv run ruff check .
uv run ruff format .
```

### Scripts

One-off maintenance scripts live in `scripts/` and run with `uv run python scripts/<name>.py` settings for the scripts is loaded from the `settings.yaml`:

- **`notify_english_named_users.py`** — messages every user whose stored profile name is
  written in English (Latin letters, no Cyrillic) and who has at least one booking in the
  last 6 months, asking them to switch their name to Russian. Flags: `--dry-run` (list
  recipients, send nothing), `--months N` (look-back window, default `6`), `--delay`
  (seconds between messages, default `0.1`).

  ```bash
  uv run python scripts/notify_english_named_users.py
  ```

- **`notify_still_using_music_room.py`** — Ask old non-banned user whether they still want to use the music room (recent users is skipped), via a Yes/No inline-keyboard poll  with addition to Russian-full-name reminder. Flags: `--dry-run` (list
  recipients, send nothing), `--delay` (seconds between messages, default `0.1`).

  ```bash
  uv run python scripts/notify_still_using_music_room.py
  ```

**Set up PyCharm integrations**

1. Run configurations ([docs](https://www.jetbrains.com/help/pycharm/run-debug-configuration.html#createExplicitly)).
   Right-click the `__main__.py` file in the project explorer, select `Run '__main__'` from the context menu.
2. Ruff ([plugin](https://plugins.jetbrains.com/plugin/20574-ruff)).
   It will lint and format your code. Make sure to enable `Use ruff format` option in plugin settings.
3. Pydantic ([plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)). It will fix PyCharm issues with
   type-hinting.
4. Conventional commits ([plugin](https://plugins.jetbrains.com/plugin/13389-conventional-commit)). It will help you
   to write [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Localization

**Aiogram:**

All localized bot messages should be wrapped: `__("Hello world"")`

1. Extract messages:
   ```bash
   uv run pybabel extract -k __ --input-dirs=. -o locales/messages.pot
   ```
2. Update translations:
   ```bash
   uv run pybabel update -i locales/messages.pot -d locales -D messages --ignore-pot-creation-date
   ```
3. Translate messages in created `.po` files
4. Compile translations:
   ```bash
   uv run pybabel compile -d locales -D messages
   ```

**Aiogram dialog:**

Add translations identifiers (strings inside `I18Format`) and their translations to `.ftl` files

### Deployment

We use Docker with the Docker Compose plugin to run the service on servers.

1. Copy the settings file: `cp settings.example.yaml settings.yaml`
2. Change settings in the `settings.yaml` file according to your needs
   (check [settings.schema.yaml](settings.schema.yaml) for more info)
3. (Optional) put database overrides in a `.env` file next to `docker-compose.yaml` — the `db` service reads
   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (all default to `postgres`) and `POSTGRES_PORT`
   (default `5432`, the host-side port). Keep `api_settings.db_url` in `settings.yaml` in sync with them.
4. Install Docker with the Docker Compose plugin
5. Build and start all services: `docker compose up --build --wait`
6. Check the logs: `docker compose logs -f`

Exposed ports: API on `localhost:8001`, Prefect UI on `localhost:4200`, PostgreSQL on `5432`, Redis on `6379`.
The `alembic-migrate` one-shot service applies migrations before the API starts.

# How to update dependencies

## Project dependencies

1. Run `uv lock --upgrade` to update the lockfile (it may update nothing, so double-check).
2. Run `uv sync` to install the updated versions.
3. Run `uv lock --upgrade-package <package>` to bump a single dependency, or
   `uv add <package>` to add a new one.

> [!NOTE]
> Keep the `prefecthq/prefect` image tag in [docker-compose.yaml](docker-compose.yaml) in sync with the
> `prefect` version in [pyproject.toml](pyproject.toml).

## Pre-commit hooks

1. Run `uv run prek auto-update`.

Also, Dependabot will help you to keep your dependencies up-to-date, see [dependabot.yml](.github/dependabot.yml).

## Contributing

We are open to contributions of any kind.
You can help us with code, bugs, design, documentation, media, new ideas, etc.
If you are interested in contributing, please read
our [contribution guide](https://github.com/one-zero-eight/.github/blob/main/CONTRIBUTING.md).
