"""
The breakout game is based on CoderDojoSV/beginner-python's tutorial

Luca Iocchi 2017
"""
import math
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Set, Tuple, Dict

import gym
import numpy as np
import pygame
from gym.spaces import Dict as DictSpace, Discrete, MultiDiscrete

Position = Tuple[int, int]

black = [0, 0, 0]
white = [255, 255, 255]
grey = [180, 180, 180]
orange = [180, 100, 20]
red = [180, 0, 0]


class PygameDrawable(ABC):

    @abstractmethod
    def draw_on_screen(self, screen: pygame.Surface):
        """Draw a Pygame object on a given Pygame screen."""


class _AbstractPygameViewer(ABC):

    @abstractmethod
    def reset(self, breakout_state: 'State'):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def close(self):
        pass


class PygameViewer(_AbstractPygameViewer):

    def __init__(self, breakout_state: 'State'):
        self.state = breakout_state

        pygame.init()
        pygame.display.set_caption('Breakout')
        self.screen = pygame.display.set_mode([self.state.config.win_width, self.state.config.win_height])
        self.myfont = pygame.font.SysFont("Arial", 30)
        self.drawables = self._init_drawables()  # type: Set[PygameDrawable]

    def reset(self, breakout_state: 'State'):
        self.state = breakout_state
        self.drawables = self._init_drawables()

    def _init_drawables(self) -> Set[PygameDrawable]:
        result = set()
        result.add(self.state.ball)
        result.add(self.state.paddle)
        result.add(self.state.brick_grid)
        return result

    def render(self, mode="human"):
        self._fill_screen()
        self._draw_score_label()
        self._draw_last_command()
        self._draw_game_objects()

        if mode == "human":
            pygame.display.update()
        elif mode == "rgb_array":
            return pygame.surfarray.array3d(self.screen)

    def _fill_screen(self):
        self.screen.fill(white)

    def _draw_score_label(self):
        score_label = self.myfont.render(str(self.state.score), 100, pygame.color.THECOLORS['black'])
        self.screen.blit(score_label, (20, 10))

    def _draw_last_command(self):
        cmd = self.state.last_command
        s = '%s' % cmd
        count_label = self.myfont.render(s, 100, pygame.color.THECOLORS['brown'])
        self.screen.blit(count_label, (60, 10))

    def _draw_game_objects(self):
        for d in self.drawables:
            d.draw_on_screen(self.screen)

    def close(self):
        pygame.display.quit()
        pygame.quit()


class BreakoutConfiguration(object):

    def __init__(self, brick_rows: int = 3,
                 brick_cols: int = 3,
                 paddle_width: int = 80,
                 paddle_height: int = 10,
                 paddle_speed: int = 10,
                 brick_width: int = 60,
                 brick_height: int = 12,
                 brick_xdistance: int = 20,
                 brick_reward: int = 5,
                 ball_radius: int = 10,
                 resolution_x: int = 20,
                 resolution_y: int = 10,
                 horizon: Optional[int] = None):
        assert brick_cols >= 3, "The number of columns must be at least three."
        self.brick_rows = brick_rows
        self.brick_cols = brick_cols
        self.paddle_width = paddle_width
        self.paddle_height = paddle_height
        self.paddle_speed = paddle_speed
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.brick_xdistance = brick_xdistance
        self.brick_reward = brick_reward
        self.ball_radius = ball_radius
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.horizon = horizon if horizon is not None else 300 * (self.brick_cols * self.brick_rows)

        self.init_ball_speed_x = 2
        self.init_ball_speed_y = 5
        self.accy = 1.00

    @property
    def win_width(self):
        return int((self.brick_width + self.brick_xdistance) * self.brick_cols + self.brick_xdistance)

    @property
    def win_height(self):
        return 480

    @property
    def n_ball_x(self):
        return self.win_width // self.resolution_x + 1

    @property
    def n_paddle_x(self):
        return self.win_width // self.resolution_x + 1

    @property
    def n_ball_y(self):
        return self.win_width // self.resolution_y + 1

    @property
    def n_ball_dir(self):
        """
        The number of possible ball directions:
        - ball going up (0-5) or down (6-9)
        - ball going left (1,2) straight (0) right (3,4)
        """
        return 10


class Command(Enum):
    NOP = 0
    LEFT = 1
    RIGHT = 2

    def __str__(self):
        cmd = Command(self.value)
        if cmd == Command.NOP:
            return "_"
        elif cmd == Command.LEFT:
            return "<"
        elif cmd == Command.RIGHT:
            return ">"
        else:
            raise ValueError("Shouldn't be here...")


class Brick(PygameDrawable):

    def __init__(self, i: int, j: int, width: int, height: int, xdistance: int,):
        self.i = i
        self.j = j
        self.width = width
        self.height = height
        self.xdistance = xdistance

        self.x = (self.width+self.xdistance)*i+self.xdistance
        self.y = 70+(self.height+8)*j
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw_on_screen(self, screen):
        pygame.draw.rect(screen, grey, self.rect, 0)


class BrickGrid(PygameDrawable):

    def __init__(self, brick_cols: int,
                 brick_rows: int,
                 brick_width: int,
                 brick_height: int,
                 brick_xdistance: int):
        self.brick_cols = brick_cols
        self.brick_rows = brick_rows
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.brick_xdistance = brick_xdistance

        self.bricks = {}  # type: Dict[Tuple[int, int], Brick]
        self.bricksgrid = np.zeros((self.brick_cols, self.brick_rows))
        self._init_bricks()

    def _init_bricks(self):
        for i in range(0, self.brick_cols):
            for j in range(0, self.brick_rows):
                temp = Brick(i, j, self.brick_width, self.brick_height, self.brick_xdistance)
                self.bricks[(i, j)] = temp
                self.bricksgrid[i][j] = 1

    def draw_on_screen(self, screen: pygame.Surface):
        for b in self.bricks.values():
            b.draw_on_screen(screen)

    def remove_brick_at_position(self, position: Position):
        self.bricks.pop(position)
        self.bricksgrid[position[0], position[1]] = 0

    def is_empty(self):
        return len(self.bricks) == 0


class Ball(PygameDrawable):

    def __init__(self, breakout_config: BreakoutConfiguration):
        self.config = breakout_config

        _initial_ball_x = self.config.win_width // 2
        _initial_ball_y = self.config.win_height - 100 - self.config.ball_radius
        self.x = _initial_ball_x
        self.y = _initial_ball_y
        self.speed_x = self.config.init_ball_speed_x
        self.speed_y = self.config.init_ball_speed_y

    @property
    def radius(self):
        return self.config.ball_radius

    def draw_on_screen(self, screen: pygame.Surface):
        pygame.draw.circle(screen, orange, [int(self.x), int(self.y)], self.radius, 0)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y


class Paddle(PygameDrawable):

    def __init__(self, breakout_config: BreakoutConfiguration):
        self.config = breakout_config

        _initial_paddle_x = self.config.win_width // 2
        _initial_paddle_y = self.config.win_height - 20
        self.x = _initial_paddle_x
        self.y = _initial_paddle_y

    @property
    def width(self):
        return self.config.paddle_width

    @property
    def height(self):
        return self.config.paddle_height

    @property
    def speed(self):
        return self.config.paddle_speed

    def draw_on_screen(self, screen: pygame.Surface):
        pygame.draw.rect(screen, grey, [self.x, self.y, self.width, self.height], 0)

    def update(self, command: Command):
        if command == Command.LEFT:
            self.x -= self.speed
        elif command == Command.RIGHT:
            self.x += self.speed
        elif command == Command.NOP:
            pass
        else:
            raise Exception("Command not recognized.")

        if self.x < 0:
            self.x = 0
        if self.x > self.config.win_width - self.width:
            self.x = self.config.win_width - self.width


class State(object):

    def __init__(self, breakout_configuration: BreakoutConfiguration):
        self.config = breakout_configuration

        self.ball = Ball(self.config)
        self.paddle = Paddle(self.config)
        self.brick_grid = BrickGrid(self.config.brick_cols,
                                    self.config.brick_rows,
                                    self.config.brick_width,
                                    self.config.brick_height,
                                    self.config.brick_xdistance)

        self.last_command = Command.NOP  # type: Command
        self.score = 0
        self._steps = 0

    def reset(self) -> 'State':
        return State(self.config)

    def update(self, command: Command):
        self.paddle.update(command)
        self.ball.update()
        self.last_command = str(command)

    def remove_brick_at_position(self, position: Position):
        self.brick_grid.remove_brick_at_position(position)

    def observe(self) -> Dict:
        """Extract the state observation based on the game configuration."""
        ball_x = int(self.ball.x) // self.config.resolution_x
        ball_y = int(self.ball.y) // self.config.resolution_y

        ball_dir = 0
        if self.ball.speed_y > 0:  # down
            ball_dir += 5
        if self.ball.speed_x < -2.5:  # quick-left
            ball_dir += 1
        elif self.ball.speed_x < 0:  # left
            ball_dir += 2
        elif self.ball.speed_x > 2.5:  # quick-right
            ball_dir += 3
        elif self.ball.speed_x > 0:  # right
            ball_dir += 4

        paddle_x = int(self.paddle.x) // self.config.resolution_x
        bricks_matrix = self.brick_grid.bricksgrid.flatten()

        return {
            "ball_x": ball_x,
            "ball_y": ball_y,
            "ball_dir": ball_dir,
            "paddle_x": paddle_x,
            "bricks_matrix": bricks_matrix,
        }

    def step(self, command: Command) -> int:
        """
        Check collisions and update the state of the game accordingly.
        :return: the reward resulting from this step.
        """
        reward = 0
        self._steps += 1
        self.update(command)

        ball = self.ball
        paddle = self.paddle

        ball_rect = pygame.Rect(ball.x - ball.radius,
                                ball.y - ball.radius,
                                ball.radius * 2,
                                ball.radius * 2)
        paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)

        # for screen border
        if ball.y < ball.radius:
            ball.y = ball.radius
            ball.speed_y = - ball.speed_y
        if ball.x < ball.radius:
            ball.x = ball.radius
            ball.speed_x = - ball.speed_x
        if ball.x > self.config.win_width - ball.radius:
            ball.x = self.config.win_width - ball.radius
            ball.speed_x = - ball.speed_x

        # for paddle
        if ball_rect.colliderect(paddle_rect):
            dbp = math.fabs(ball.x - (paddle.x + paddle.width // 2))
            if dbp < 20:
                # print 'straight'
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

            ball.speed_y = - abs(ball.speed_y)

        for brick in self.brick_grid.bricks.values():
            if brick.rect.colliderect(ball_rect):
                self.score += self.config.brick_reward
                self.remove_brick_at_position((brick.i, brick.j))
                ball.speed_y = - ball.speed_y
                reward += self.config.brick_reward
                break

        return reward

    def is_finished(self):
        end1 = self.ball.y > self.config.win_height - self.ball.radius
        end2 = self.brick_grid.is_empty()
        end3 = self._steps > self.config.horizon * self.config.brick_cols
        return end1 or end2


class DefaultBreakoutConfiguration(BreakoutConfiguration):

    def __init__(self):
        super().__init__()


class Breakout(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, breakout_config: Optional[BreakoutConfiguration] = None):

        self.config = DefaultBreakoutConfiguration() if breakout_config is None else breakout_config
        self.state = State(self.config)
        self.viewer = None  # type: Optional[PygameViewer]

        self.observation_space = DictSpace({
            "ball_x": Discrete(self.config.n_ball_x),
            "ball_y": Discrete(self.config.n_ball_y),
            "ball_dir": Discrete(self.config.n_ball_dir),
            "paddle_x": Discrete(self.config.n_paddle_x),
            "bricks_matrix": MultiDiscrete([2] * self.config.brick_cols * self.config.brick_rows)
        })

        self.action_space = Discrete(len(Command))

    def step(self, action: int):
        command = Command(action)
        reward = self.state.step(command)
        state = self.state.observe()
        is_finished = self.state.is_finished()
        info = {}
        return state, reward, is_finished, info

    def reset(self):
        self.state = State(self.config)
        if self.viewer is not None:
            self.viewer.reset(self.state)
        return self.state.observe()

    def render(self, mode='human'):
        if self.viewer is None:
            self.viewer = PygameViewer(self.state)

        return self.viewer.render(mode=mode)

    def close(self):
        if self.viewer is not None:
            self.viewer.close()


if __name__ == '__main__':
    config = BreakoutConfiguration(brick_rows=3, brick_cols=3)
    env = Breakout(config)
    env.reset()
    env.render(mode="human")
    done = False
    while not done:
        time.sleep(0.01)
        env.render(mode="human")
        obs, r, done, info = env.step(env.action_space.sample())  # take a random action
    env.close()
