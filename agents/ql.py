from agents.base import BaseAgent
from agents.utils.q_table import (
    select_max_action,
    select_q_value,
    select_max_q_value,
    insert_q_value,
    select_q_values_table,
)


class QLAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.compiled = True

        self.action_history = []
        self.observation_history = []
        self.next_observation_history = []

        # Hyperparameters
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1 if self.training else 0

    def forward(self, observation):
        legal_actions = self._get_legal_actions(observation)
        fallback_action = legal_actions[self.np_random.choice(len(legal_actions))]

        if self.np_random.uniform(0, 1) < self.epsilon:
            # Explore action space.
            action = fallback_action

        else:
            # Exploit learned values.
            action = select_max_action(observation)
            if action not in self._get_legal_actions(observation):
                action = fallback_action

        # Book-keeping.
        self.action_history.append(action)
        self.observation_history.append(observation)

        return action

    def backward(self, reward, terminal=False):
        if len(self.observation_history) > 1:
            next_observation = self.observation_history.pop()
            next_action = self.action_history.pop()
            self._maximize_q_value(next_observation, reward)
            self.observation_history.append(next_observation)
            self.action_history.append(next_action)

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
