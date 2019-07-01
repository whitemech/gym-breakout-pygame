# -*- coding: utf-8 -*-

"""Breakout environments using a "normal" state space.
- BreakoutNMultiDiscrete
- BreakoutNDiscrete
"""

from typing import Optional

import numpy as np
from gym.spaces import Discrete, MultiDiscrete

from gym_breakout_pygame.breakout_env import Breakout, BreakoutConfiguration, BreakoutState
from gym_breakout_pygame.utils import encode


class BreakoutNMultiDiscrete(Breakout):
    """
    Breakout env with a gym.MultiDiscrete observation space composed by:
    - paddle x position
    - ball x position
    - ball y position
    - ball direction

    """

    def __init__(self, config: Optional[BreakoutConfiguration] = None):
        super().__init__(config)
        self.observation_space = MultiDiscrete((
            self._paddle_x_space.n,
            self._ball_x_space.n,
            self._ball_y_space.n,
            self._ball_dir_space.n
        ))

    @classmethod
    def observe(cls, state: BreakoutState):
        paddle_x = state.paddle.x // state.config.resolution_x
        ball_x = state.ball.x // state.config.resolution_x
        ball_y = state.ball.y // state.config.resolution_y
        ball_dir = state.ball.dir

        obs = [paddle_x, ball_x, ball_y, ball_dir]
        return np.asarray(obs)


class BreakoutNDiscrete(Breakout):
    """
    The same of BreakoutNMultiDiscrete, but the observation space encoded in one integer.
    """

    def __init__(self, config: Optional[BreakoutConfiguration] = None):
        super().__init__(config)
        self.observation_space = Discrete(config.n_paddle_x * config.n_ball_x * config.n_ball_y * config.n_ball_dir)

    @classmethod
    def observe(cls, state: BreakoutState):
        obs = BreakoutNMultiDiscrete.observe(state)
        dims = [state.config.n_paddle_x, state.config.n_ball_x, state.config.n_ball_y, state.config.n_ball_dir]
        return encode(list(obs), dims)
