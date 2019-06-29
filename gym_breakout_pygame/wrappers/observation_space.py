import time
from typing import Optional

import gym
import numpy as np
from gym.spaces import Discrete, MultiDiscrete

from gym_breakout_pygame.breakout_env import Breakout, BreakoutConfiguration
from gym_breakout_pygame.utils import encode


class BreakoutN(gym.ObservationWrapper):
    """
    Breakout env with observation space composed by:
    - paddle x position
    - ball x position
    - ball y position
    - ball direction

    """

    def __init__(self, breakout_config: Optional[BreakoutConfiguration] = None, encode=True):
        super().__init__(Breakout(breakout_config))

        self._encode = encode
        self._wrapped_obs_space = self._wrap_obs_space(encode=False)

        self.observation_space = self._wrap_obs_space(encode=self._encode)

    def _wrap_obs_space(self, encode=False):
        obs_space = self.env.observation_space

        wrapped_obs_space = MultiDiscrete((
            obs_space["paddle_x"].n,
            obs_space["ball_x"].n,
            obs_space["ball_y"].n,
            obs_space["ball_dir"].n,
        ))

        if encode:
            wrapped_obs_space = Discrete(np.prod(wrapped_obs_space.nvec))

        return wrapped_obs_space

    def observation(self, observation):

        ball_x = observation["ball_x"]
        ball_y = observation["ball_y"]
        ball_dir = observation["ball_dir"]
        paddle_x = observation["paddle_x"]

        if self._encode:
            wrapped_obs = encode([paddle_x, ball_x, ball_y, ball_dir], self._wrapped_obs_space.nvec)
            return wrapped_obs
        else:
            return np.asarray([paddle_x, ball_x, ball_y, ball_dir])


if __name__ == '__main__':
    config = BreakoutConfiguration(brick_rows=3, brick_cols=3)
    env = BreakoutN(config)
    env.reset()
    env.render(mode="human")
    print("Obs space: ", env.observation_space)
    print("Act space: ", env.action_space)
    done = False
    while not done:
        time.sleep(0.01)
        env.render(mode="human")
        obs, r, done, info = env.step(env.action_space.sample())  # take a random action
    env.close()
