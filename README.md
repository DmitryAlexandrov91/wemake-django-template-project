# team-climate

Team Climate 380

This project was generated with [`wemake-django-template`](https://github.com/wemake-services/wemake-django-template). Current template version is: [59ce134](https://github.com/wemake-services/wemake-django-template/tree/59ce13457de11f5020e11df98b9b4ef22ec1d116). See what is [updated](https://github.com/wemake-services/wemake-django-template/compare/59ce13457de11f5020e11df98b9b4ef22ec1d116...master) since then.


[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake-services.github.io)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)


## Prerequisites

You will need:

- `python3.12` (see `pyproject.toml` for exact version), use `pyenv install`
- `postgresql` (see `docker-compose.yml` for exact version)
- Latest `docker`


## Development

When developing locally, we use:

- [`editorconfig`](http://editorconfig.org/) plugin (**required**)
- [`poetry`](https://github.com/python-poetry/poetry) (**required**)
- [`pyenv`](https://github.com/pyenv/pyenv)


## Documentation

Full documentation is available here: [`docs/`](docs).


### Установка зависимостей при помощи poetry

1. Установите пакетный менеджер poetry
2. Установите pyton 3.12.11(рекомендую познакомится с менеджером uv *https://habr.com/ru/articles/828016/*)
3. Создайте окружение для poetry. 
Используя команду `poetry env use` укажите путь где лежит ваш python 3.12.11

В моём случае выглядело так:

```bash
poetry env use  /home/aldmal/snap/code/204/.local/share/uv/python/cpython-3.12.11-linux-x86_64-gnu/bin/python3.12

```

4. Командой `poetry install` установите зависимости для проекта.
5. Введите в терминале `poetry` чтобы увидеть список доступных команд.
