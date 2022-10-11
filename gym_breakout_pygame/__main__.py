#!/usr/bin/env python3
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

"""Run a short demo.

Example of usage:

    python3 gym_breakout_pygame --rows 3 --columns 3 --fire --record

"""
import argparse
import time
from argparse import ArgumentParser
from datetime import datetime

from gym.wrappers.monitoring.video_recorder import VideoRecorder

from gym_breakout_pygame.breakout_env import Breakout, BreakoutConfiguration
from gym_breakout_pygame.wrappers.dict_space import BreakoutDictSpace


def parse_arguments() -> argparse.Namespace:
    """Parse arguments."""
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=3, help="Number of rows")
    parser.add_argument("--columns", type=int, default=3, help="Number of columns")
    parser.add_argument("--fire", action="store_true", help="Enable fire.")
    parser.add_argument("--disable-ball", action="store_true", help="Disable the ball.")
    parser.add_argument("--record", action="store_true", help="Record a video.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="videos/" + str(datetime.now()),
        help="Video directory.",
    )
    parser.add_argument("--random", action="store_true", help="Play randomly")

    return parser.parse_args()


def _play_randomly(env: Breakout) -> None:  # pylint: disable=redefined-outer-name
    env.reset()
    env.render(mode="human")
    done = False
    while not done:
        time.sleep(0.01)
        env.render(mode="human")
        _ = env.step(env.action_space.sample())  # take a random action
    env.close()


if __name__ == "__main__":
    args = parse_arguments()
    config = BreakoutConfiguration(
        brick_rows=args.rows,
        brick_cols=args.columns,
        fire_enabled=args.fire,
        ball_enabled=not args.disable_ball,
    )
    env = BreakoutDictSpace(config)
    if args.record:
        env = VideoRecorder(env, args.output_dir)

    if args.random:
        _play_randomly(env)
    else:
        env.play()
