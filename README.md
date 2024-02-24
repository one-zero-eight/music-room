# InNoHassle Music room

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-MusicRoom&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-MusicRoom)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-MusicRoom&metric=bugs)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-MusicRoom)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-MusicRoom&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-MusicRoom)

1. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Install dependencies
    ```bash
   poetry install --no-root
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
