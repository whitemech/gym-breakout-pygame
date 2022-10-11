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


"""A Gym wrapper that repeats the same action until the observation does not change."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from gym_breakout_pygame.breakout_env import Breakout, BreakoutConfiguration


class BreakoutSkipper(Breakout, ABC):
    """Repeat same step until a different observation is obtained."""

    def __init__(self, breakout_config: Optional[BreakoutConfiguration] = None):
        """Initialize the environment."""
        super().__init__(breakout_config)
        self._previous_obs = None  # type: Any

    @classmethod
    @abstractmethod
    def compare(cls, obs1, obs2) -> bool:
        """Compare two observations."""
        return False

    def reset(self, seed: Optional[int] = None, **kwargs) -> Any:
        """Reset the environment."""
        obs = super().reset(seed=seed, **kwargs)
        self._previous_obs = obs
        return obs

    def step(self, action: int) -> Tuple[Any, float, bool, Any]:
        """Do a simulation step in the environment."""
        obs, reward, is_finished, info = super().step(action)
        while self.compare(obs, self._previous_obs) and not is_finished:
            next_obs, next_reward, next_is_finished, next_info = super().step(action)
            obs = next_obs
            reward += next_reward
            is_finished = is_finished or next_is_finished
            info.update(next_info)

        self._previous_obs = obs
        return obs, reward, is_finished, info
