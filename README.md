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


### Installing dependencies using Poetry

1. Install the package manager Poetry.
2. Install Python 3.12.11 with poetry env install command, or use pyenv.
3. Create an environment for Poetry.
Use the command `poetry env use` to specify the path where your Python 3.12.11 is located.

In my case it looked like this:

```bash
poetry env use  /home/aldmal/snap/code/204/.local/share/uv/python/cpython-3.12.11-linux-x86_64-gnu/bin/python3.12

```

4. Run the command `poetry install` to install project dependencies.
5. Type `poetry` in the terminal to see a list of available commands.
