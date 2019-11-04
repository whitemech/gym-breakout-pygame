# -*- coding: utf-8 -*-

"""Breakout environments using a "dict" state space."""

from gym.spaces import Dict

from gym_breakout_pygame.breakout_env import BreakoutState
from gym_breakout_pygame.wrappers.skipper import BreakoutSkipper


class BreakoutDictSpace(BreakoutSkipper):
    """A Breakout environment with a dictionary state space.
    The components of the space are:
    - Paddle x coordinate (Discrete)
    - Ball x coordinate (Discrete)
    - Ball y coordinate (Discrete)
    - Ball horizontal speed (Discrete)
    - Ball vertical speed (Discrete)
    - Brick matrix (MultiBinary)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observation_space = Dict({
            "paddle_x": self._paddle_x_space,
            "ball_x": self._ball_x_space,
            "ball_y": self._ball_y_space,
            "ball_x_speed": self._ball_x_speed_space,
            "ball_y_speed": self._ball_y_speed_space,
            "bricks_matrix": self._bricks_matrix_space,
        })

    def observe(self, state: BreakoutState):
        """Observe the state."""
        return state.to_dict()

    @classmethod
    def compare(cls, obs1, obs2) -> bool:
        """Compare two observations."""
        # return obs1 == obs2
        return False
