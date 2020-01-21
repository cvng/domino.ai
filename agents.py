"""
Author: Cedric Vangout <mail@cvng.dev>
Gym Environment: cvng/Domino-v0
Permalink: https://github.com/cvng/domino.ai
"""

import numpy as np

from domino.domino import possibilities, dtoa, atod, pack
from q_table import (
    insert_q_value,
    select_max_q_value,
    select_q_value,
    select_q_values_table,
    select_max_action,
)


class BaseAgent:
    def __init__(self, action_space, np_random=None):
        self.np_random = np_random
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


class HumanAgent(BaseAgent):
    def act(self, observation, reward, done):
        legal_actions = self._get_legal_actions(observation)
        description = "\n".join(
            ["%s: %s" % (action, atod(action)) for action in sorted(legal_actions)]
        )
        action = None
        while action not in legal_actions:
            action = int(input("%s\nEnter your value: " % description))
        return action


class RandomAgent(BaseAgent):
    def act(self, observation, reward, done):
        legal_actions = self._get_legal_actions(observation)
        return legal_actions[self.np_random.choice(len(legal_actions))]


class TrainableAgent(RandomAgent):
    def __init__(self, training=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.action_history = []
        self.observation_history = []
        self.next_observation_history = []

        # Hyperparameters
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1 if training else 0

    def act(self, observation, reward, done):
        fallback_action = super().act(observation, reward, done)

        if self.np_random.uniform(0, 1) < self.epsilon:
            # Explore action space.
            action = fallback_action

        else:
            # Exploit learned values.
            action = select_max_action(observation)
            if action not in self._get_legal_actions(observation):
                action = fallback_action

        if self.observation_history:
            self._maximize_q_value(observation, reward)

        # Book-keeping.
        self.action_history.append(action)
        self.observation_history.append(observation)

        return action

    def _maximize_q_value(self, next_observation, reward):
        if self.next_observation_history:
            assert self.observation_history[-1] == self.next_observation_history[-1]

        observation, action = self.observation_history[-1], self.action_history[-1]

        old_q_value = select_q_value(observation, action) or 0

        next_max_q_value = select_max_q_value(next_observation) or 0

        new_q_value = (1 - self.alpha) * old_q_value + self.alpha * (
            reward + self.gamma * next_max_q_value
        )

        insert_q_value(observation, action, new_q_value)

        self.next_observation_history.append(next_observation)

        return True

    @property
    def q_table(self):
        return select_q_values_table()
