# -*- coding: utf-8 -*-
"""Run a short demo.

Example of usage:

    python3 gym_breakout_pygame --rows 3 --columns 3 --fire --record

"""
import time
from argparse import ArgumentParser
from datetime import datetime

from gym.wrappers import Monitor

from gym_breakout_pygame.breakout_env import BreakoutConfiguration
from gym_breakout_pygame.wrappers.dict_space import BreakoutDictSpace


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=3, help="Number of rows")
    parser.add_argument("--columns", type=int, default=3, help="Number of columns")
    parser.add_argument("--fire", action="store_true", help="Enable fire.")
    parser.add_argument("--record", action="store_true", help="Record a video.")
    parser.add_argument("--output-dir", type=str, default="videos/" + str(datetime.now()), help="Video directory.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    config = BreakoutConfiguration(brick_rows=args.rows, brick_cols=args.columns, fire_enabled=args.fire)
    env = BreakoutDictSpace(config)
    if args.record:
        env = Monitor(env, args.output_dir)

    env.reset()
    env.render(mode="human")
    done = False
    while not done:
        time.sleep(0.01)
        env.render(mode="human")
        obs, r, done, info = env.step(env.action_space.sample())  # take a random action
    env.close()
