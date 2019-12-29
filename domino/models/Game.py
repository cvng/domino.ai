import logging
from random import shuffle
from time import sleep

from .Player import Player
from ..constants import DOMINOES, PLAYERS, DELAY
from ..strategies import tested_strategy

logger = logging.getLogger(__name__)


class Game:
    def __init__(self):
        self.winner = None
        self.table = []
        self.players = []

    def run(self):
        """
        Run Domino Gameplay in 4 stages.
        """
        self.randomize()
        self.distribute()
        self.loop()
        self.shut()

    def randomize(self):
        """
        1 - Randomization with hardcoded-rules.
        """
        logger.info("\n\n--> Randomization")

        self.table = DOMINOES.copy()
        shuffle(self.table)

        logger.info("Game.table: %s" % len(self.table))

    def distribute(self):
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

            player = Player(i, strategy=strategy)

            while len(player.hand) < dominoes_per_player:
                player.pick(self.table.pop())

            assert len(player.hand) == dominoes_per_player

            logger.info(player)

            self.players.append(player)

        assert len(self.table) == 0

    def loop(self):
        """
        3 - Game loop with turn-by-turn.
        """
        logger.info("\n\n--> Game loop")

        locked_counter = 0

        while self.winner is None:
            for player in self.players:
                logger.info("\nGame.table: %s" % self.table)
                logger.info(player)

                sleep(DELAY)

                # Decide what to play next
                result = player.play(table=self.table)

                # Can we play?
                if result:
                    logger.info("%s --> PLAY! %s" % (player, result))
                    locked_counter = 0  # reset counter

                    domino_to_play, index_to_insert = result

                    # Run checks
                    assert domino_to_play not in self.table
                    assert domino_to_play[::-1] not in self.table
                    if self.table and index_to_insert == 0:
                        assert domino_to_play[-1] == self.table[0][0]
                    elif self.table and index_to_insert == -1:
                        assert domino_to_play[0] == self.table[-1][1]

                    # Play
                    self.table.insert(index_to_insert, domino_to_play)

                    if self.table and len(self.table) > 1:
                        for i in range(len(self.table) - 1):
                            assert self.table[i][1] == self.table[i + 1][0]

                # Has nothing changed?
                else:
                    logger.info("%s --> PASS! %s" % (player, result))
                    locked_counter = locked_counter + 1  # inc counter

                # Do we have a winner?
                if len(player.hand) == 0:
                    logger.info("GAME END! And the winner is...")
                    self.winner = player
                    break

                # Is the game locked?
                if locked_counter >= len(self.players):
                    break

            if locked_counter >= len(self.players):
                logger.info("game_locked: GAME LOCKED!")
                ranking = sorted(self.players, key=lambda p: p.total)
                self.winner = ranking[-1]
                break

    def shut(self):
        """
        4 - Game end.
        """
        logger.info("\n\n--> Game end")

        logger.info(
            "Winner: Player %s: %s %s"
            % (self.winner.id, self.winner.hand, self.winner.total)
        )

        return self.winner.id
