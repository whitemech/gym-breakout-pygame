import time
from functools import reduce
from typing import Optional

import gym
from gym.spaces import Dict, Discrete

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
        self._discrete_spaces = [self._wrapped_obs_space["ball_x"],
                                 self._wrapped_obs_space["ball_y"],
                                 self._wrapped_obs_space["ball_dir"],
                                 self._wrapped_obs_space["paddle_x"]]

        self.observation_space = self._wrap_obs_space(encode=self._encode)

    def _wrap_obs_space(self, encode=False):
        obs_space = self.env.observation_space

        wrapped_obs_space = Dict({
            "ball_x": obs_space["ball_x"],
            "ball_y": obs_space["ball_y"],
            "ball_dir": obs_space["ball_dir"],
            "paddle_x": obs_space["paddle_x"],
        })

        if encode:
            discrete_spaces = list(wrapped_obs_space.spaces.values())
            max_n = reduce(lambda x, y: x * y, [d.n for d in discrete_spaces])
            wrapped_obs_space = Discrete(max_n)

        return wrapped_obs_space

    def observation(self, observation):

        ball_x = observation["ball_x"]
        ball_y = observation["ball_y"]
        ball_dir = observation["ball_dir"]
        paddle_x = observation["paddle_x"]

        if self._encode:
            wrapped_obs = encode([ball_x, ball_y, ball_dir, paddle_x],
                                 self._discrete_spaces)
            return wrapped_obs
        else:
            return {
                "ball_x": ball_x,
                "ball_y": ball_y,
                "ball_dir": ball_dir,
                "paddle_x": paddle_x,
            }


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
        print(obs)
    env.close()
