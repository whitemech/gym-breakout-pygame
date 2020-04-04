# gym-breakout-pygame

[![PyPI](https://img.shields.io/pypi/v/gym_breakout_env)](https://pypi.org/project/gym_breakout_env/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gym_breakout_env)
[![](https://img.shields.io/pypi/l/aea)](https://github.com/fetchai/agents-aea/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aea)
![Codecov](https://img.shields.io/codecov/c/github/whitemech/gym_breakout_env)
![CI](https://github.com/whitemech/gym_breakout_env/workflows/CI/badge.svg?branch=master)

Gym Breakout environment using Pygame.

## Preliminaries

## Install

Install with `pip`:

    pip3 install gym_breakout_pygame==0.1.0
    
Or, install from source:

    git clone https://github.com/sapienza-rl/gym-breakout-pygame.git
    cd gym-breakout-pygame
    pip install .

## Development

- clone the repo:

      git clone https://github.com/sapienza-rl/gym-breakout-pygame.git
      cd gym-breakout-pygame
    
- Create/activate the virtual environment:

      pipenv shell --python=python3.7
    
- Run a short demo:

      python gym_breakout_pygame --record
      
Check for an `.mp4` file in `videos/`. You should get:

<p align="center">
  <img width="260" height="480" src="https://raw.githubusercontent.com/sapienza-rl/gym-breakout-pygame/develop/docs/breakout-example.gif"></p>


- Enable fire:

      python gym_breakout_pygame --fire

<p align="center">
  <img width="260" height="480" src="https://raw.githubusercontent.com/sapienza-rl/gym-breakout-pygame/develop/docs/breakout-example-fire.gif">
</p>

## Tests

TODO

## License

MIT License.

## Credits

The code is largely inspired by [RLGames](https://github.com/iocchi/RLGames.git)

