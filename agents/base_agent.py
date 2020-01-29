"""
Author: Cedric Vangout <mail@cvng.dev>
Gym Environment: cvng/Domino-v0
Permalink: https://github.com/cvng/domino.ai
"""

import numpy as np
from gym.utils import seeding

from envs.domino import possibilities, dtoa, atod, pack


class BaseAgent:
    def __init__(self, training=True, action_space=None, np_random=None):
        self.training = training
        self.np_random = np_random or seeding.np_random()[0]
        self.action_space = action_space

    def act(self, observation, reward, done):
        raise NotImplementedError

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
