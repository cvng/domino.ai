from agents.base_agent import BaseAgent


class RandomAgent(BaseAgent):
    def act(self, observation, reward, done):
        legal_actions = self._get_legal_actions(observation)
        return legal_actions[self.np_random.choice(len(legal_actions))]
