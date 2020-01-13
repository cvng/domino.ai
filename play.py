import logging
import time
from collections import Counter

from domino.domino import DominoEnv, possibilities, _action_to_domino, _domino_to_action

logger = logging.getLogger(__name__)

logging.basicConfig(level="INFO")


def play(episodes=1, max_steps=99):
    env = DominoEnv()
    agent = RandomAgent(env.action_space)
    history = []
    for i_episode in range(episodes):
        observation = env.reset()
        reward = 0
        done = False
        logger.info("observation=%s reward=%s done=%s" % (observation, reward, done))

        for i_step in range(max_steps):
            env.render()

            action = agent.act(observation, reward, done, np_random=env.np_random)
            logger.info("action=%s" % action)

            observation, reward, done, info = env.step(action)
            logger.info(
                "observation=%s reward=%s done=%s" % (observation, reward, done)
            )

            time.sleep(3)
            if done:
                history.append(env.current_turn)
                logger.info(
                    "DONE! episodes=%s steps=%s history=%s"
                    % (i_episode + 1, i_step + 1, dict(Counter(history)))
                )
                break
    env.close()


class RandomAgent:
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done, np_random=None):
        table, hand = self._parse_obs(observation)
        choices = possibilities(table, hand)
        if len(choices):
            action = _domino_to_action(choices[np_random.choice(len(choices))])
        else:
            action = 0
        return action

    def _parse_obs(self, observation):
        hand = [_action_to_domino(i + 1) for i, v in enumerate(observation) if v == 1]

        table_partial = [
            _action_to_domino(i + 1) for i, v in enumerate(observation) if v == 2
        ]

        first_domino = [
            _action_to_domino(i + 1) for i, v in enumerate(observation) if v == 3
        ]
        if not first_domino:
            first_domino = [
                _action_to_domino(i + 1)[::-1]
                for i, v in enumerate(observation)
                if v == 4
            ]

        last_domino = [
            _action_to_domino(i + 1) for i, v in enumerate(observation) if v == 5
        ]
        if not last_domino:
            last_domino = [
                _action_to_domino(i + 1)[::-1]
                for i, v in enumerate(observation)
                if v == 6
            ]

        table = first_domino + table_partial + last_domino

        return table, hand


if __name__ == "__main__":
    play()
