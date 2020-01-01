import logging
from time import sleep

from .constants import DOMINOES, PLAYERS, DELAY
from .state import (
    table_init,
    table_shuffle,
    player_add,
    get_players,
    get_table,
    table_insert,
    set_winner,
    get_winner,
    player_pick,
    player_init,
    get_player,
    player_play,
    get_last_move,
    get_winner_total,
    get_ranking,
)
from .strategies import tested_strategy

logger = logging.getLogger(__name__)


def game_run():
    """
    Run Domino Gameplay in 4 stages.
    """
    game_randomize()
    game_distribute()
    game_loop()
    game_shut()


def game_randomize():
    """
    1 - Randomization with hardcoded-rules.
    """
    logger.info("\n\n--> Randomization")

    table_init(dominoes=DOMINOES.copy())
    table_shuffle()

    logger.info("Game.table: %s" % len(get_table()))


def game_distribute():
    """
    2 - Distribution with no-pick.
    """
    logger.info("\n\n--> Distribution")

    dominoes_per_player = len(DOMINOES) / PLAYERS

    logger.info("PLAYERS: %s" % PLAYERS)
    logger.info("dom_per_player: %s" % dominoes_per_player)

    for i in range(1, PLAYERS + 1):
        strategy = None
        if i == 1:
            strategy = tested_strategy

        player = player_init(i, strategy=strategy) and get_player(i)

        while len(player["hand"]) < dominoes_per_player:
            player_pick(i)

        assert len(player["hand"]) == dominoes_per_player

        logger.info(player)

        player_add(i, player)

    assert len(get_table()) == 0


def game_loop():
    """
    3 - Game loop with turn-by-turn.
    """
    logger.info("\n\n--> Game loop")

    locked_counter = 0

    while get_winner() is None:
        for player in get_players():
            logger.info("\nGame.table: %s" % get_table())
            logger.info(player)

            sleep(DELAY)

            # Decide what to play next
            result = player_play(player["id"]) and get_last_move()

            # Can we play?
            if result:
                logger.info("%s --> PLAY! %s" % (player, result))
                locked_counter = 0  # reset counter

                domino_to_play, index_to_insert = result

                # Run checks
                assert domino_to_play not in get_table()
                assert domino_to_play[::-1] not in get_table()
                if get_table() and index_to_insert == 0:
                    assert domino_to_play[-1] == get_table()[0][0]
                elif get_table() and index_to_insert == -1:
                    assert domino_to_play[0] == get_table()[-1][1]

                # Play
                table_insert(index_to_insert, domino_to_play)

                if get_table() and len(get_table()) > 1:
                    for i in range(len(get_table()) - 1):
                        assert get_table()[i][1] == get_table()[i + 1][0]

            # Has nothing changed?
            else:
                logger.info("%s --> PASS! %s" % (player, result))
                locked_counter = locked_counter + 1  # inc counter

            # Do we have a winner?
            if len(player["hand"]) == 0:
                logger.info("GAME END! And the winner is...")
                set_winner(player)
                break

            # Is the game locked?
            if locked_counter >= len(get_players()):
                break

        if locked_counter >= len(get_players()):
            logger.info("game_locked: GAME LOCKED!")
            ranking = get_ranking()
            set_winner(ranking[-1])
            break


def game_shut():
    """
    4 - Game end.
    """
    logger.info("\n\n--> Game end")

    logger.info(
        "Winner: Player %s: %s %s"
        % (get_winner()["id"], get_winner()["hand"], get_winner_total())
    )

    return get_winner()["id"]
