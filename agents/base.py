"""
Author: Cedric Vangout <mail@cvng.dev>
Gym Environment: cvng/Domino-v0
Permalink: https://github.com/cvng/domino.ai
"""

import numpy as np
from gym.utils import seeding
from rl.core import Agent

from envs.domino import possibilities, dtoa, atod, pack


class BaseAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.np_random, seed = seeding.np_random()

    def _get_legal_actions(self, observation):
        table, hand = self._parse_obs(observation)
        actions = [dtoa(domino) for domino in possibilities(table, hand)]

        reversed_hand = [domino[::-1] for domino in hand]
        extra_actions = [dtoa(domino) for domino in possibilities(table, reversed_hand)]
        if extra_actions:
            actions += extra_actions

        actions = list(set(actions))
        if not actions:
            actions = [0]
        return actions

    def _parse_obs(self, observation, pack_size=len(pack)):
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.unravel_index.html
        observation = np.unravel_index(observation, dims=(*(3,) * pack_size, 7, 7))

        hand = [atod(i + 1) for i, v in enumerate(observation[:pack_size]) if v == 1]

        table = [atod(i + 1) for i, v in enumerate(observation[:pack_size]) if v == 2]

        if table:
            leftmost_n, rightmost_n = observation[pack_size], observation[pack_size + 1]
            first_domino, last_domino = [(leftmost_n, None)], [(None, rightmost_n)]
        else:
            first_domino, last_domino = [], []

        table = first_domino + table + last_domino

        return table, hand

    def forward(self, observation):
        raise NotImplementedError()

    def backward(self, reward, terminal):
        pass

    def compile(self, optimizer, metrics=[]):
        pass

    def load_weights(self, filepath):
        pass

    def save_weights(self, filepath, overwrite=False):
        pass

    @property
    def layers(self):
        pass
