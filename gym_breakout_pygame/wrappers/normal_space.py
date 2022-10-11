# MIT License
#
# Copyright (c) 2019-2022 Marco Favorito, Luca Iocchi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


"""
Breakout environments using a "normal" state space.

Two types:
- BreakoutNMultiDiscrete: the observation state is MultiDiscrete;
- BreakoutNDiscrete: the observation state is Discrete.
"""

from typing import Optional

import gym
import numpy as np
from gym.spaces import Discrete, MultiDiscrete
from numpy._typing import NDArray

from gym_breakout_pygame.breakout_env import BreakoutConfiguration, BreakoutState
from gym_breakout_pygame.utils import encode
from gym_breakout_pygame.wrappers.skipper import BreakoutSkipper


class BreakoutNMultiDiscrete(BreakoutSkipper):
    """
    Breakout with multi-discrete state space.

    Breakout env with a gym.MultiDiscrete observation space composed by:

    - paddle x position
    - ball x position
    - ball y position
    - ball direction
    """

    def __init__(self, config: Optional[BreakoutConfiguration] = None) -> None:
        """Initialize the environment."""
        super().__init__(config)
        self.observation_space = MultiDiscrete(
            [
                self._paddle_x_space.n,
                self._ball_x_space.n,
                self._ball_y_space.n,
                self._ball_x_speed_space.n,
                self._ball_y_speed_space.n,
            ]
        )

    @classmethod
    def compare(cls, obs1: np.ndarray, obs2: np.ndarray) -> bool:
        """Compare two observations."""
        return (obs1 == obs2).all()

    def observe(self, state: BreakoutState) -> gym.Space:  # pylint: disable=no-self-use
        """Return a vectorized observation."""
        return self.observe_multidiscrete(state)

    @staticmethod
    def observe_multidiscrete(state: BreakoutState) -> NDArray[np.int]:
        """Observe from state a multidiscrete set of features."""
        paddle_x = state.paddle.x // state.config.resolution_x
        ball_x = state.ball.x // state.config.resolution_x
        ball_y = state.ball.y // state.config.resolution_y
        ball_x_speed = state.ball.speed_x_norm
        ball_y_speed = state.ball.speed_y_norm

        obs = [paddle_x, ball_x, ball_y, ball_x_speed, ball_y_speed]
        return np.asarray(obs)


class BreakoutNDiscrete(BreakoutSkipper):
    """
    Breakout with discrete state space.

    The same of BreakoutNMultiDiscrete, but the observation space encoded in only one integer.
    """

    def __init__(self, config: Optional[BreakoutConfiguration] = None) -> None:
        """Initialize the environment."""
        super().__init__(config)
        self.observation_space = Discrete(
            self.config.n_paddle_x
            * self.config.n_ball_x
            * self.config.n_ball_y
            * self.config.n_ball_x_speed
            * self.config.n_ball_y_speed
        )

    def observe(self, state: BreakoutState) -> int:
        """Do an observation of the environment state."""
        obs = list(map(int, BreakoutNMultiDiscrete.observe_multidiscrete(state)))
        dims = [
            state.config.n_paddle_x,
            state.config.n_ball_x,
            state.config.n_ball_y,
            state.config.n_ball_x_speed,
            state.config.n_ball_y_speed,
        ]
        result = encode(list(obs), dims)
        return result

    @classmethod
    def compare(cls, obs1, obs2) -> bool:
        """Compare two observations."""
        return obs1 == obs2
