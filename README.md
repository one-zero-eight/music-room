# InNoHassle-MusicRoom

1. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Install dependencies
    ```bash
   poetry install --no-root --with dev
   ```
3. Setup settings

   Run
   ```bash
   cp settings.example.yaml settings.yaml
   ```
   And edit settings.yaml
4. Run app
   ```bash
   poetry run python -m src.api
   ```
   Or
   ```bash
   poetry run uvicorn src.api.app:app --use-colors --proxy-headers --forwarded-allow-ips=*
   ```
