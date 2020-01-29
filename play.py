import argparse
import logging
import time
from collections import Counter

from agents import TrainableAgent
from domino import DominoEnv

logger = logging.getLogger(__name__)

logging.basicConfig(level="INFO")


def play(episodes=10000, training=True, debug=False):
    env = DominoEnv(n_players=1)
    history = []
    time_start = time.time()

    for i_episode in range(episodes):
        # env.seed(0)

        agents_args = (training, env.action_space)
        agents = [
            TrainableAgent(*agents_args),
            # RandomAgent(*agents_args),
            # TrainableAgent(*agents_args),
            # TrainableAgent(*agents_args),
        ]

        observation, reward, done, info = env.reset(), 0, False, {}
        logger.debug("observation=%s reward=%s done=%s" % (observation, reward, done))

        i_step = 0
        while not done:
            env.render(mode="human" if debug else None)

            current_turn = i_step % len(agents)
            agent = agents[current_turn]

            action = agent.act(observation, reward, done)
            logger.debug("action=%s" % action)

            observation, reward, done, info = env.step(action)
            logger.debug(
                "observation=%s reward=%s done=%s" % (observation, reward, done)
            )

            if done:
                env.render(mode="human" if debug else None)

                agent.act(observation, reward, done)  # reward agent

                history.append(
                    current_turn if reward > 0 else -1  # 1 if reward == -10 else -1
                )
                ranking = [
                    "%s: %s%% (%s)" % (k, round(100 * v / (i_episode + 1), 2), v)
                    for k, v in sorted(Counter(history).items())
                ]

                if (i_episode + 1) % 100 == 0:
                    time_elapsed = round(time.time() - time_start, 2)
                    logger.info(
                        "DONE! episodes=%s steps=%s time_elapsed=%s ranking=%s"
                        % (i_episode + 1, i_step + 1, time_elapsed, ranking)
                    )
                break

            time.sleep(1 if debug else 0)
            i_step += 1

    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episodes", type=int, nargs="?")
    args = parser.parse_args()
    play(*[arg for arg in vars(args).values() if arg])
