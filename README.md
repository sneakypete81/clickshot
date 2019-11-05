# Clickshot

[![PyPI](https://img.shields.io/pypi/v/clickshot.svg)](https://pypi.python.org/pypi/clickshot)
[![Build Status](https://travis-ci.com/sneakypete81/clickshot.svg?branch=master)](https://travis-ci.com/sneakypete81/clickshot)

Easy GUI testing with [pyautogui](https://github.com/asweigart/pyautogui).

## Installation

```sh
pip install clickshot
pip install opencv-python # Recommended for best performance
```

Pyautogui is installed automatically, but see the
[pyautogui install documentation](https://pyautogui.readthedocs.io/en/latest/install.html)
for platform-specific dependencies that you may need to install manually.

## Usage

TODO

## Development

Requires [Poetry](https://poetry.eustace.io/).

```sh
git clone https://github.com/sneakypete81/clickshot.git
poetry install
```

Then you can use the following:

```sh
  poetry run pytest # Run all unit tests
  poetry run flake8 # Run the linter
  poetry run tox    # Run all checks across all supported Python versions
  poetry shell      # Open a venv shell with your local clone installed
```
