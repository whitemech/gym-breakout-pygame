<h1 align="center">
  <b>gym-breakout-pygame</b>
</h1>

<p align="center">
  <a href="https://pypi.org/project/gym-breakout-pygame">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/gym-breakout-pygame">
  </a>
  <a href="https://pypi.org/project/gym-breakout-pygame">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/gym-breakout-pygame" />
  </a>
  <a href="">
    <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/gym-breakout-pygame" />
  </a>
  <a href="">
    <img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/gym-breakout-pygame">
  </a>
  <a href="">
    <img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/gym-breakout-pygame">
  </a>
  <a href="https://github.com/whitemech/gym-breakout-pygame/blob/master/LICENSE">
    <img alt="GitHub" src="https://img.shields.io/github/license/whitemech/gym-breakout-pygame">
  </a>
</p>
<p align="center">
  <a href="">
    <img alt="test" src="https://github.com/whitemech/gym-breakout-pygame/workflows/test/badge.svg">
  </a>
  <a href="">
    <img alt="lint" src="https://github.com/whitemech/gym-breakout-pygame/workflows/lint/badge.svg">
  </a>
  <a href="">
    <img alt="docs" src="https://github.com/whitemech/gym-breakout-pygame/workflows/docs/badge.svg">
  </a>
  <a href="https://codecov.io/gh/whitemech/gym-breakout-pygame">
    <img alt="codecov" src="https://codecov.io/gh/whitemech/gym-breakout-pygame/branch/master/graph/badge.svg?token=FG3ATGP5P5">
  </a>
</p>


Gym Breakout environment using Pygame.

## Install

Install with `pip`:

    pip3 install gym_breakout_pygame
    
Or, install from source:

    git clone https://github.com/whitemech/gym-breakout-pygame.git
    cd gym-breakout-pygame
    pip install .


## Development

- clone the repo:

        git clone https://github.com/whitemech/gym-breakout-pygame.git
        cd gym-breakout-pygame
    
- Create/activate the virtual environment (using Poetry):

        poetry shell
        poetry install
    
- Run a short demo:

        python gym_breakout_pygame --random --record
      
Check for an `.mp4` file in `videos/`. You should get:

<p align="center">
  <img width="260" height="480" src="https://raw.githubusercontent.com/whitemech/gym-breakout-pygame/develop/docs/breakout-example.gif"></p>


- Enable fire:

        python gym_breakout_pygame --fire

<p align="center">
  <img width="260" height="480" src="https://raw.githubusercontent.com/whitemech/gym-breakout-pygame/develop/docs/breakout-example-fire.gif">
</p>


## Tests

To run tests: `tox`

To run only the code tests: `tox -e py3.10`

To run only the linters: 
- `tox -e flake8`
- `tox -e mypy`
- `tox -e black-check`
- `tox -e isort-check`

Please look at the `tox.ini` file for the full list of supported commands. 

## Docs

To build the docs: `mkdocs build`

To view documentation in a browser: `mkdocs serve`
and then go to [http://localhost:8000](http://localhost:8000)

## License

gym-breakout-pygame is released under the GNU General Public License v3.0 or later (GPLv3+).

Copyright 2019-2022 Marco Favorito, Luca Iocchi

## Authors

- [Marco Favorito](https://marcofavorito.me/)
- [Luca Iocchi](https://github.com/iocchi)

The code is largely inspired by [RLGames](https://github.com/iocchi/RLGames.git)

