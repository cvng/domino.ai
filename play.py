import logging
import time

from domino.domino import DominoEnv

logger = logging.getLogger(__name__)

logging.basicConfig(level="INFO")


def play(episodes=1, max_steps=99):
    env = DominoEnv()
    for i_episode in range(episodes):
        observation = env.reset()
        logger.info("observation=%s" % observation)

        for i_step in range(max_steps):
            env.render()

            action = env.action_space.sample()
            logger.info("action=%s" % action)

            observation, reward, done, info = env.step(action)
            logger.info("observation=%s" % observation)
            logger.info("reward=%s" % reward)
            logger.info("done=%s" % done)
            logger.info("info=%s" % info)

            time.sleep(1)
            if done:
                logger.info("DONE! episodes=%s steps=%s" % (i_episode + 1, i_step + 1))
                break
    env.close()


if __name__ == "__main__":
    play()
