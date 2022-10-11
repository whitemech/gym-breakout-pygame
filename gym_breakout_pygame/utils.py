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

"""This module contains utility functions."""
from functools import reduce
from typing import List


def encode(obs: List[int], spaces: List[int]) -> int:
    """
    Encode an observation from a list of gym.Discrete spaces in one number.

    :param obs: an observation belonging to the state space (a list of gym.Discrete spaces)
    :param spaces: the list of gym.Discrete spaces from where the observation is observed.
    :return: the encoded observation.
    """
    assert len(obs) == len(spaces)
    sizes = spaces
    result = obs[0]
    shift = sizes[0]
    for observation, size in list(zip(obs, sizes))[1:]:
        result += observation * shift
        shift *= size

    return result


def decode(obs: int, spaces: List[int]) -> List[int]:
    """
    Decode an observation from a list of gym.Discrete spaces in a list of integers.

    It assumes that obs has been encoded by using the 'utils.encode' function.

    :param obs: the encoded observation
    :param spaces: the list of gym.Discrete spaces from where the observation is observed.
    :return: the decoded observation.
    """
    result = []
    sizes = spaces[::-1]
    shift = reduce(lambda x, y: x * y, sizes) // sizes[0]
    for size in sizes[1:]:
        quotient = obs // shift
        result.append(quotient)
        obs %= shift
        shift //= size

    result.append(obs)
    return result[::-1]
