import logging
from operator import itemgetter

from domino.game import game_run
from domino.state import get_winner, game_init

logger = logging.getLogger(__name__)

logging.basicConfig(level="INFO")


def run(runs=1):
    history = {}

    for _ in range(runs):
        game_init()
        game_run()
        winner = get_winner()
        if not history.get(winner["id"]):
            history[winner["id"]] = 0
        history[winner["id"]] = history[winner["id"]] + 1

    logger.info("\n\n--> Summary:")
    logger.info("%s" % history)

    for k, v in sorted(history.items(), key=itemgetter(1)):
        logger.info("Player #%s: %s victories" % (k, v))


if __name__ == "__main__":
    run()
