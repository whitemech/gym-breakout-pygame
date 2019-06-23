from setuptools import setup, find_packages

setup(
    name='gym_breakout_pygame',
    version='0.0.1',
    keywords='environment, agent, rl, openaigym, openai-gym, gym, breakout',
    url='https://github.com/sapienza-rl/gym-breakout-pygame',
    description='Gym Breakout environment using Pygame',
    packages=find_packages("gym_breakout_pygame*"),
    install_requires=["gym", "pygame"],
    zip_safe=False
)
