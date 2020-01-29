from agents.base import BaseAgent


class RandomAgent(BaseAgent):
    def forward(self, observation):
        legal_actions = self._get_legal_actions(observation)
        return legal_actions[self.np_random.choice(len(legal_actions))]
