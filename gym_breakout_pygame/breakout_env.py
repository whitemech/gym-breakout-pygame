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
The breakout game is based on CoderDojoSV/beginner-python's tutorial.

Luca Iocchi 2017
"""
import dataclasses
import math
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Set, Tuple, cast

import gym
import numpy as np
import pygame
from gym.spaces import Discrete, MultiBinary
from gym.utils.seeding import np_random

Position = Tuple[int, int]

black = [0, 0, 0]
white = [255, 255, 255]
grey = [180, 180, 180]
orange = [180, 100, 20]
red = [180, 0, 0]


class PygameDrawable(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class of a drawable Pygame object."""

    @abstractmethod
    def draw_on_screen(self, screen: pygame.Surface) -> None:
        """Draw a Pygame object on a given Pygame screen."""


class _AbstractPygameViewer(ABC):
    """Abstract base class for viewable object."""

    @abstractmethod
    def reset(self, breakout_state: "BreakoutState") -> None:
        """Reset the viewer."""

    @abstractmethod
    def render(self) -> None:
        """Render a frame of the game."""

    @abstractmethod
    def close(self) -> None:
        """Close the viewer."""


class PygameViewer(_AbstractPygameViewer):
    """A concrete Pygame viewer class."""

    def __init__(self, breakout_state: "BreakoutState") -> None:
        """Initialize the Pygame viewer object."""
        self.state = breakout_state

        pygame.init()  # pylint: disable=no-member
        pygame.display.set_caption("Breakout")
        self.screen = pygame.display.set_mode(
            [self.state.config.win_width, self.state.config.win_height]
        )
        self.myfont = pygame.font.SysFont("Arial", 30)
        self.drawables = self._init_drawables()  # type: Set[PygameDrawable]

    def reset(self, breakout_state: "BreakoutState") -> None:
        """Reset the viewer."""
        self.state = breakout_state
        self.drawables = self._init_drawables()

    def _init_drawables(self) -> Set[PygameDrawable]:
        """Initialize the drawable objects."""
        result: Set[PygameDrawable] = set()
        result.add(self.state.ball)
        result.add(self.state.paddle)
        result.add(self.state.brick_grid)
        result.add(self.state.bullet)
        return result

    def render(self, mode="human") -> None:
        """Render a frame of the game."""
        self._fill_screen()
        self._draw_score_label()
        self._draw_last_command()
        self._draw_game_objects()

        if mode == "human":
            pygame.display.update()
        elif mode == "rgb_array":
            screen = pygame.surfarray.array3d(self.screen)
            # swap width with height
            screen.swapaxes(0, 1)

    def _fill_screen(self) -> None:
        """Fill the screen with white color."""
        self.screen.fill(white)

    def _draw_score_label(self) -> None:
        """Draw the score label."""
        score_label = self.myfont.render(
            str(self.state.score),
            100,
            pygame.color.THECOLORS["black"],  # pylint: disable=c-extension-no-member
        )
        self.screen.blit(score_label, (50, 10))

    def _draw_last_command(self) -> None:
        """Draw the last command executed."""
        cmd = self.state.last_command
        cmd_to_string = str(cmd)
        count_label = self.myfont.render(
            cmd_to_string,
            100,
            pygame.color.THECOLORS["brown"],  # pylint: disable=c-extension-no-member
        )
        self.screen.blit(count_label, (20, 10))

    def _draw_game_objects(self) -> None:
        """Draw the game objects."""
        for drawable in self.drawables:
            drawable.draw_on_screen(self.screen)

    def close(self) -> None:
        """Close the viewer."""
        pygame.display.quit()
        pygame.quit()  # pylint: disable=no-member


@dataclasses.dataclass(frozen=True)
class BreakoutConfiguration:  # pylint: disable=too-many-instance-attributes
    """A dataclass for the breakout configuration."""

    brick_rows: int = 3
    brick_cols: int = 3
    paddle_width: int = 80
    paddle_height: int = 10
    paddle_speed: int = 10
    brick_width: int = 60
    brick_height: int = 12
    brick_xdistance: int = 20
    brick_reward: float = 5.0
    step_reward: float = -0.01
    game_over_reward: float = -10.0
    ball_radius: int = 10
    resolution_x: int = 20
    resolution_y: int = 10
    horizon: Optional[int] = None
    fire_enabled: bool = False
    ball_enabled: bool = True
    complex_bump: bool = False
    deterministic: bool = True

    init_ball_speed_x: float = 2.0
    init_ball_speed_y: float = 5.0
    accy: float = 1.00

    def __post_init__(self) -> None:
        """Do post-initialization checks."""
        assert self.brick_cols >= 3, "The number of columns must be at least three."
        assert self.brick_rows >= 1, "The number of columns must be at least three."
        assert (
            self.fire_enabled or self.ball_enabled
        ), "Either fire or ball must be enabled."
        super().__setattr__(
            "horizon",
            self.horizon
            if self.horizon is not None
            else 300 * (self.brick_cols * self.brick_rows),
        )

    @property
    def win_width(self) -> int:
        """Return the window width."""
        return int(
            (self.brick_width + self.brick_xdistance) * self.brick_cols
            + self.brick_xdistance
        )

    @property
    def win_height(self) -> int:
        """Get the window height."""
        return 480

    @property
    def n_ball_x(self) -> int:
        """Return the number of values for the x-position of the ball."""
        return self.win_width // self.resolution_x + 1

    @property
    def n_paddle_x(self) -> int:
        """Return the number of values for the x-position of the paddle."""
        return self.win_width // self.resolution_x + 1

    @property
    def n_ball_y(self) -> int:
        """Return the number of values for the y-position of the ball."""
        return self.win_height // self.resolution_y + 1

    @property
    def n_ball_dir(self) -> int:
        """
        Return the number of possible ball directions.

        - ball going up (0-5) or down (6-9)
        - ball going left (1,2) straight (0) right (3,4)

        :return: the total number of possible directions.
        """
        return 10

    @property
    def n_ball_x_speed(self) -> int:
        """Return the number of speed values for the x component of the ball."""
        return 5

    @property
    def n_ball_y_speed(self) -> int:
        """Return the number of speed values for the y component of the ball."""
        return 2


class Command(Enum):
    """Enumeration of possible player commands."""

    NOP = 0
    LEFT = 1
    RIGHT = 2
    FIRE = 3

    def __str__(self) -> str:
        """Get the string representation."""
        cmd = Command(self.value)
        if cmd == Command.NOP:
            return "_"
        if cmd == Command.LEFT:
            return "<"
        if cmd == Command.RIGHT:
            return ">"
        if cmd == Command.FIRE:
            return "o"
        raise ValueError("Shouldn't be here...")


class Brick(
    PygameDrawable
):  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Class to represent a brick Pygame object."""

    def __init__(
        self,
        i: int,
        j: int,
        width: int,
        height: int,
        xdistance: int,
    ) -> None:
        """Initialize the brick object."""
        self.i = i
        self.j = j
        self.width = width
        self.height = height
        self.xdistance = xdistance

        self.x = (  # pylint: disable=invalid-name
            self.width + self.xdistance
        ) * i + self.xdistance
        self.y = 70 + (self.height + 8) * j  # pylint: disable=invalid-name
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw_on_screen(self, screen: pygame.Surface) -> None:
        """Draw the object on the screen."""
        pygame.draw.rect(screen, grey, self.rect, 0)


class BrickGrid(PygameDrawable):
    """Class to represent the brick grid."""

    def __init__(
        self,
        brick_cols: int,
        brick_rows: int,
        brick_width: int,
        brick_height: int,
        brick_xdistance: int,
    ):
        """Initialize the brick grid object."""
        self.brick_cols = brick_cols
        self.brick_rows = brick_rows
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.brick_xdistance = brick_xdistance

        self.bricks = {}  # type: Dict[Tuple[int, int], Brick]
        self.bricksgrid = np.zeros((self.brick_cols, self.brick_rows))
        self._init_bricks()

    def _init_bricks(self) -> None:
        """Initialize the grid of bricks."""
        for i in range(0, self.brick_cols):
            for j in range(0, self.brick_rows):
                temp = Brick(
                    i, j, self.brick_width, self.brick_height, self.brick_xdistance
                )
                self.bricks[(i, j)] = temp
                self.bricksgrid[i][j] = 1

    def draw_on_screen(self, screen: pygame.Surface) -> None:
        """Draw the bricks on the screen."""
        for brick in self.bricks.values():
            brick.draw_on_screen(screen)

    def remove_brick_at_position(self, position: Position) -> None:
        """Remove the brick at a given position."""
        self.bricks.pop(position)
        self.bricksgrid[position[0], position[1]] = 0

    def is_empty(self) -> bool:
        """Return true if the grid of bricks is empty."""
        return len(self.bricks) == 0


class Ball(PygameDrawable):
    """Class to represent the ball object."""

    def __init__(self, breakout_config: BreakoutConfiguration) -> None:
        """Initialize the ball object."""
        self.config = breakout_config

        if breakout_config.ball_enabled:
            _initial_ball_x = self.config.win_width // 2
            _initial_ball_y = self.config.win_height - 100 - self.config.ball_radius
            self.x: float = _initial_ball_x  # pylint: disable=invalid-name
            self.y: float = _initial_ball_y  # pylint: disable=invalid-name
            self.speed_x = self.config.init_ball_speed_x
            self.speed_y = self.config.init_ball_speed_y
            self._radius = self.config.ball_radius
        else:
            self.x = 0.0
            self.y = 0.0
            self.speed_x = 0.0
            self.speed_y = 0.0
            self._radius = 0

    @property
    def radius(self) -> int:
        """Get the radius of the ball."""
        return self._radius

    @property
    def speed_x_norm(self) -> int:
        """Get the normalized x-speed."""
        if self.speed_x < -2.5:
            return 0
        if -2.5 <= self.speed_x < 0:
            return 1
        if self.speed_x == 0:
            return 2
        if 0 < self.speed_x < 2.5:
            return 3
        if 2.5 <= self.speed_x:
            return 4
        raise ValueError("Speed x not recognized.")

    @property
    def speed_y_norm(self) -> int:
        """Get the normalized y-speed."""
        if self.speed_y <= 0:
            return 0
        return 1

    @property
    def dir(self) -> int:
        """Get the direction index of the ball."""
        ball_dir = 0
        if self.speed_y > 0:  # down
            ball_dir += 5
        if self.speed_x < -2.5:  # quick-left
            ball_dir += 1
        elif self.speed_x < 0:  # left
            ball_dir += 2
        elif self.speed_x > 2.5:  # quick-right
            ball_dir += 3
        elif self.speed_x > 0:  # right
            ball_dir += 4
        return ball_dir

    def draw_on_screen(self, screen: pygame.Surface) -> None:
        """Draw the Pygame object on the screen."""
        pygame.draw.circle(screen, orange, [int(self.x), int(self.y)], self.radius, 0)

    def update(self) -> None:
        """Update the position of the ball according to the speed."""
        self.x += self.speed_x
        self.y += self.speed_y


class Paddle(PygameDrawable):
    """Class to represent the paddle object."""

    def __init__(self, breakout_config: BreakoutConfiguration) -> None:
        """Initialize the paddle object."""
        self.config = breakout_config

        _initial_paddle_x = self.config.win_width // 2
        _initial_paddle_y = self.config.win_height - 20
        self.x = _initial_paddle_x  # pylint: disable=invalid-name
        self.y = _initial_paddle_y  # pylint: disable=invalid-name

    @property
    def width(self) -> int:
        """Get the paddle width."""
        return self.config.paddle_width

    @property
    def height(self) -> int:
        """Get the paddle height."""
        return self.config.paddle_height

    @property
    def speed(self) -> int:
        """Get the paddle speed."""
        return self.config.paddle_speed

    def draw_on_screen(self, screen: pygame.Surface) -> None:
        """Draw the object on screen."""
        pygame.draw.rect(screen, grey, [self.x, self.y, self.width, self.height], 0)

    def update(self, command: Command) -> None:
        """Update the position of the paddle."""
        if command == Command.LEFT:
            self.x -= self.speed
        elif command == Command.RIGHT:
            self.x += self.speed
        elif command == Command.NOP:
            pass
        elif command == Command.FIRE:
            pass
        else:
            raise Exception("Command not recognized.")

        self.x = max(self.x, 0)
        if self.x > self.config.win_width - self.width:
            self.x = self.config.win_width - self.width


class Bullet(PygameDrawable):
    """Class to represent a bullet object."""

    def __init__(self, breakout_config: BreakoutConfiguration) -> None:
        """Initialize the bullet object."""
        self.config = breakout_config

        self.x = 0.0  # pylint: disable=invalid-name
        self.y = 0.0  # pylint: disable=invalid-name
        self.speed_y = 0.0

    @property
    def in_movement(self) -> bool:
        """Return true if the bullet is in movement."""
        return self.speed_y < 0.0

    @property
    def width(self) -> int:
        """Get the width of the bullet."""
        return 5

    @property
    def height(self) -> int:
        """Get the height of the bullet."""
        return 5

    def update(self) -> None:
        """Update the position of the bullet."""
        self.y += self.speed_y
        if self.y < 5:
            self.reset()

    def reset(self) -> None:
        """Reset the state of the bullet."""
        self.x = 0.0
        self.y = 0.0
        self.speed_y = 0.0

    def draw_on_screen(self, screen: pygame.Surface) -> None:
        """Draw the object on the screen."""
        if self.speed_y < 0:
            pygame.draw.rect(screen, red, [self.x, self.y, self.width, self.height], 0)


class BreakoutState:  # pylint: disable=too-many-instance-attributes
    """Class to represent the Breakout game state."""

    def __init__(
        self,
        breakout_configuration: BreakoutConfiguration,
        random_event_gen: Optional["RandomEventGenerator"] = None,
    ) -> None:
        """Initialize the Breakout state object."""
        self.config = breakout_configuration

        self.ball = Ball(self.config)
        self.paddle = Paddle(self.config)
        self.brick_grid = BrickGrid(
            self.config.brick_cols,
            self.config.brick_rows,
            self.config.brick_width,
            self.config.brick_height,
            self.config.brick_xdistance,
        )

        self.bullet = Bullet(self.config)

        self.last_command: Command = Command.NOP
        self.score = 0.0
        self._steps = 0

        self._random_event_gen = (
            RandomEventGenerator() if random_event_gen is None else random_event_gen
        )

    def reset(self) -> "BreakoutState":
        """Reset the Breakout state."""
        return BreakoutState(self.config, self._random_event_gen)

    def update(self, command: Command) -> None:
        """Update the Breakout state according to the provided command."""
        self.paddle.update(command)
        self.ball.update()
        self.bullet.update()
        self.last_command = command

    def remove_brick_at_position(self, position: Position) -> None:
        """Remove brick at a certain position."""
        self.brick_grid.remove_brick_at_position(position)

    def to_dict(self) -> Dict:
        """Extract the state observation based on the game configuration."""
        ball_x = int(self.ball.x) // self.config.resolution_x
        ball_y = int(self.ball.y) // self.config.resolution_y
        ball_x_speed = self.ball.speed_x_norm
        ball_y_speed = self.ball.speed_y_norm
        paddle_x = int(self.paddle.x) // self.config.resolution_x
        bricks_matrix = self.brick_grid.bricksgrid

        return {
            "paddle_x": paddle_x,
            "ball_x": ball_x,
            "ball_y": ball_y,
            "ball_x_speed": ball_y_speed,
            "ball_y_speed": ball_x_speed,
            "bricks_matrix": bricks_matrix,
        }

    def step(  # noqa: C901 # pylint: disable=too-many-branches,too-many-statements
        self, command: Command
    ) -> float:
        """
        Check collisions and update the state of the game accordingly.

        :param command: the command chosen by the player
        :return: the reward resulting from this step.
        """
        reward = 0.0
        self._steps += 1
        self.update(command)

        ball = self.ball
        paddle = self.paddle
        bullet = self.bullet
        brick_grid = self.brick_grid

        ball_rect = pygame.Rect(
            ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2
        )
        paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
        bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)

        # for screen border
        if ball.y < ball.radius:
            ball.y = ball.radius
            ball.speed_y = -ball.speed_y
            if np.isclose(ball.speed_x, 0.0):
                ball.speed_x = 1.0 * random.choice([-1.0, 1.0])
        if ball.x < ball.radius:
            ball.x = ball.radius
            ball.speed_x = -ball.speed_x
        if ball.x > self.config.win_width - ball.radius:
            ball.x = self.config.win_width - ball.radius
            ball.speed_x = -ball.speed_x

        # for paddle
        if ball_rect.colliderect(paddle_rect):
            if self.config.complex_bump:
                dbp = math.fabs(ball.x - (paddle.x + paddle.width / 2))
                if dbp < 20:
                    if ball.speed_x < -5:
                        ball.speed_x += 2
                    elif ball.speed_x > 5:
                        ball.speed_x -= 2
                    elif ball.speed_x <= -0.5:
                        ball.speed_x += 0.5
                    elif ball.speed_x >= 0.5:
                        ball.speed_x -= 0.5

                dbp = math.fabs(ball.x - (paddle.x + 0))
                if dbp < 10:
                    ball.speed_x = -abs(ball.speed_x) - 1
                dbp = math.fabs(ball.x - (paddle.x + paddle.width))
                if dbp < 10:
                    ball.speed_x = abs(ball.speed_x) + 1

            else:
                dbp = math.fabs(ball.x - (paddle.x + paddle.width / 2))
                if dbp < 20:
                    if ball.speed_x != 0:
                        ball.speed_x = 2 * abs(ball.speed_x) / ball.speed_x
                dbp = math.fabs(ball.x - (paddle.x + 0))
                if dbp < 20:
                    ball.speed_x = -5
                    self._random_event_gen.perturbate_ball_speed_after_paddle_hit(self)
                dbp = math.fabs(ball.x - (paddle.x + paddle.width))
                if dbp < 20:
                    ball.speed_x = 5
                    self._random_event_gen.perturbate_ball_speed_after_paddle_hit(self)

            ball.speed_y = -abs(ball.speed_y)

        for brick in brick_grid.bricks.values():
            if brick.rect.colliderect(ball_rect):
                self.score += self.config.brick_reward
                self.remove_brick_at_position((brick.i, brick.j))
                ball.speed_y = -ball.speed_y
                reward += self.config.brick_reward
                break

        if command == Command.FIRE:  # fire
            if not bullet.in_movement:
                bullet.x = paddle.x + paddle.width / 2
                bullet.y = paddle.y
                bullet.speed_y = -10

        # firing
        if bullet.y < 5:
            # reset
            bullet.reset()

        for brick in brick_grid.bricks.values():
            if brick.rect.colliderect(bullet_rect):
                self.remove_brick_at_position((brick.i, brick.j))
                reward += self.config.brick_reward
                self.score += self.config.brick_reward
                self.bullet.reset()
                break

        reward += self.config.step_reward

        # ball out
        reward += (
            self.config.game_over_reward
            if self.ball.y > self.config.win_height - self.ball.radius
            else 0
        )
        # time out
        reward += (
            self.config.game_over_reward
            if self._steps > cast(int, self.config.horizon)
            else 0.0
        )

        return reward

    def is_finished(self) -> bool:
        """Check whether the game is over."""
        end1 = self.ball.y > self.config.win_height - self.ball.radius
        end2 = self.brick_grid.is_empty()
        end3 = self._steps > cast(int, self.config.horizon)
        return end1 or end2 or end3

    def set_seed(self, seed: int) -> None:
        """Set the random seed."""
        self._random_event_gen = RandomEventGenerator(seed)


class RandomEventGenerator:
    """Class to wrap a random number generator."""

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize the random event generator."""
        self._seed = seed
        self._rng = np_random(self._seed)[0]

    def perturbate_initial_ball_speed(self, state: BreakoutState) -> None:
        """Perturbate the initial ball speed randomly."""
        if not state.config.deterministic:
            ran = self._rng.uniform(0.75, 1.5)
            state.ball.speed_x *= ran
            # print(print("random ball_speed_x = %.2f" %self.ball_speed_x)

    def perturbate_ball_speed_after_brick_hit(self, state: BreakoutState) -> None:
        """Perturbate the ball speed after a brick hit."""
        if not state.config.deterministic:
            ran = self._rng.uniform(0.0, 1.0)
            if ran < 0.5:
                state.ball.speed_x *= -1

    def perturbate_ball_speed_after_paddle_hit(self, state: BreakoutState) -> None:
        """Perturbate ball speed after a paddle hit."""
        if not state.config.deterministic:
            ran = self._rng.uniform(0.0, 1.0)
            if ran < 0.1:
                state.ball.speed_x *= 0.75
            elif ran > 0.9:
                state.ball.speed_x *= 1.5
            sign = state.ball.speed_x / abs(state.ball.speed_x)
            state.ball.speed_x = min(state.ball.speed_x, 6) * sign
            state.ball.speed_x = max(state.ball.speed_x, 0.5) * sign


class Breakout(gym.Env, ABC):  # pylint: disable=too-many-instance-attributes
    """A generic Breakout env. The feature space must be defined in subclasses."""

    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(self, breakout_config: Optional[BreakoutConfiguration] = None) -> None:
        """Initialize the Breakout Gym environment."""
        self.config = (
            BreakoutConfiguration() if breakout_config is None else breakout_config
        )
        self.state = BreakoutState(self.config)
        self.viewer = None  # type: Optional[PygameViewer]

        self.action_space = Discrete(
            len(Command) if self.config.fire_enabled else len(Command) - 1
        )

        self._paddle_x_space = Discrete(self.config.n_paddle_x)
        self._ball_x_space = Discrete(self.config.n_ball_x)
        self._ball_y_space = Discrete(self.config.n_ball_y)
        self._ball_x_speed_space = Discrete(self.config.n_ball_x_speed)
        self._ball_y_speed_space = Discrete(self.config.n_ball_y_speed)
        self._ball_dir_space = Discrete(self.config.n_ball_dir)
        self._bricks_matrix_space = MultiBinary(
            (self.config.brick_rows, self.config.brick_cols)
        )

    def step(self, action: int) -> Tuple[Any, float, bool, Any]:
        """Do a simulation step in the environment."""
        command = Command(action)
        reward = self.state.step(command)
        obs = self.observe(self.state)
        is_finished = self.state.is_finished()
        info: Dict = {}
        return obs, reward, is_finished, info

    def reset(self, seed: Optional[int] = None, **_kwargs) -> Any:
        """Reset the environment."""
        self.state = self.state.reset()
        if seed is not None:
            self.state.set_seed(seed)
        if self.viewer is not None:
            self.viewer.reset(self.state)
        return self.observe(self.state)

    def render(self, mode="human") -> None:
        """Render the state of the environment."""
        if self.viewer is None:
            self.viewer = PygameViewer(self.state)

        return self.viewer.render(mode=mode)

    def close(self) -> None:
        """Close the environment."""
        if self.viewer is not None:
            self.viewer.close()

    @abstractmethod
    def observe(self, state: BreakoutState) -> gym.Space:
        """
        Extract observation from the state of the game.

        :param state: the state of the game
        :return: an instance of a gym.Space
        """

    def play(self) -> None:
        """Do a playing session."""
        self.reset()
        self.render()
        quitted = False
        while not quitted:
            pygame.time.wait(10)
            cmd = 0
            events = pygame.event.get()
            for event in events:
                if (
                    event.type == pygame.KEYDOWN  # pylint: disable=no-member
                    and event.key == pygame.K_q  # pylint: disable=no-member
                ):
                    quitted = True

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LEFT]:  # pylint: disable=no-member
                cmd = 1
            elif pressed[pygame.K_RIGHT]:  # pylint: disable=no-member
                cmd = 2
            elif pressed[pygame.K_SPACE]:  # pylint: disable=no-member
                cmd = 3

            _, _, done, _ = self.step(cmd)
            if done:
                self.reset()
            self.render()
