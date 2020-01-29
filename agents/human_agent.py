from agents.base_agent import BaseAgent
from envs.domino import atod


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
