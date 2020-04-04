# gym-breakout-pygame

[![PyPI](https://img.shields.io/pypi/v/gym_breakout_pygame)](https://pypi.org/project/gym_breakout_pygame/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gym_breakout_pygame)
[![](https://img.shields.io/pypi/l/gym_breakout_pygame)](https://github.com/whitemech/gym-breakout-pygame/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dm/gym_breakout_pygame)
![CI](https://github.com/whitemech/gym-breakout-pygame/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/whitemech/gym-breakout-pygame/branch/master/graph/badge.svg)](https://codecov.io/gh/whitemech/gym-breakout-pygame)

Gym Breakout environment using Pygame.

## Links

- GitHub: [https://github.com/whitemech/gym-breakout-pygame](https://github.com/whitemech/gym-breakout-pygame)
- PyPI: [https://pypi.org/project/gym_breakout_pygame/](https://pypi.org/project/gym_breakout_pygame/)
- Documentation: [https://whitemech.github.io/gym-breakout-pygame](https://whitemech.github.io/gym-breakout-pygame)
- Changelog: [https://whitemech.github.io/gym-breakout-pygame/history/](https://whitemech.github.io/gym-breakout-pygame/history/)
- Issue Tracker:[https://github.com/whitemech/gym-breakout-pygame/issues](https://github.com/whitemech/gym-breakout-pygame/issues)
- Download: [https://pypi.org/project/gym_breakout_pygame/#files](https://pypi.org/project/gym_breakout_pygame/#files)

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
    
- Create/activate the virtual environment:

        pipenv shell --python=python3.7
    
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

We use `tox` for testing:

```
tox -e py3.x
```
Replace `x` depending on the minor version of your Python interpreter. E.g.
`tox -e py3.7`

## Credits

The code is largely inspired by [RLGames](https://github.com/iocchi/RLGames.git)

