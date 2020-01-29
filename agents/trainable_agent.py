from agents.random_agent import RandomAgent
from agents.utils.q_table import (
    select_max_action,
    select_q_value,
    select_max_q_value,
    insert_q_value,
    select_q_values_table,
)


class TrainableAgent(RandomAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.action_history = []
        self.observation_history = []
        self.next_observation_history = []

        # Hyperparameters
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1 if self.training else 0

    def act(self, observation, reward, done):
        fallback_action = super().act(observation, reward, done)

        if self.np_random.uniform(0, 1) < self.epsilon:
            # Explore action space.
            action = fallback_action

        # elif select_max_q_value(observation) == 0:
        # Explore action with no values.
        # action = fallback_action

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
