"""
Author: Cedric Vangout <mail@cvng.dev>
Gym Environment: cvng/Domino-v0
Permalink: https://github.com/cvng/domino.ai
"""

import gym
from gym import spaces
from gym.utils import seeding

pack: list = [
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 5),
    (0, 6),
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (3, 3),
    (3, 4),
    (3, 5),
    (3, 6),
    (4, 4),
    (4, 5),
    (4, 6),
    (5, 5),
    (5, 6),
    (6, 6),
]


def valid_move(table: list, hand: list, indice: [int, None]) -> bool:
    """
    >>> valid_move([0], [1, 2, 3, 4, 5, 6, 7], 0)
    False
    >>> valid_move([0], [1, 2, 3, 4, 5, 6, 7], 8)
    False
    >>> valid_move([], [0, 2, 3, 4, 5, 6, 7], 2)
    False
    >>> valid_move([0], [1, 2, 3, 4, 5, 6, 7], 7)
    False
    >>> valid_move([0], [1, 2, 3, 4, 5, 6, 7], None)
    False
    >>> valid_move([], [0, 2, 3, 4, 5, 6, 7], 0)
    True
    """

    # domino already played
    if indice in table:
        return False

    # domino not in hand
    if indice not in hand:
        return False

    # domino to be played first is (0, 0) aka pack[0]
    if len(table) == 0 and indice != 0:
        return False

    # domino do not match what is on table
    if insert_index(table, indice) is None:
        return False

    # domino should be played if possible
    if indice is None and len(possibilities(table, hand)) > 0:
        return False

    return True


def insert_index(table: list, indice: int) -> [int, None]:
    """
    >>> insert_index([], 0)
    0
    >>> insert_index([0], 1)
    0
    >>> insert_index([0, 1], 7)
    2
    >>> insert_index([0], 7) is None
    True
    """
    if len(table) == 0:
        return 0

    first_domino = _indice_to_domino(table[0])
    last_domino = _indice_to_domino(table[-1])
    domino = _indice_to_domino(indice)

    if first_domino[0] in domino:
        return 0

    if last_domino[1] in domino:
        return len(table)

    return None


def possibilities(table: list, hand: list):
    """
    >>> possibilities([0], [1, 2, 3, 4, 5, 6, 7])
    [1, 2, 3, 4, 5, 6]
    """
    return [indice for indice in hand if insert_index(table, indice) is not None]


def _domino_to_indice(domino: tuple) -> int:
    """
    >>> _domino_to_indice((0,0))
    0
    >>> _domino_to_indice((1, 0))
    1
    """
    try:
        return pack.index(domino)
    except ValueError:
        return pack.index(domino[::-1])


def _indice_to_domino(indice: int) -> tuple:
    """
    >>> _indice_to_domino(0)
    (0, 0)
    >>> _indice_to_domino(1)
    (0, 1)
    """
    return pack[indice]


class DominoEnv(gym.Env):
    """Simple domino environment

    Dominoes is a family of tile-based games played with rectangular "domino" tiles.

    Each domino is a rectangular tile with a line dividing its face into two square ends.
    Each end is marked with a number of spots (also called pips, nips, or dobs) or is blank.
    The backs of the dominoes in a set are indistinguishable, either blank or having some common design.

    The domino gaming pieces make up a domino set, sometimes called a deck or pack.
    The traditional Sino-European domino set consists of 28 dominoes,
    featuring all combinations of spot counts between zero and six.
    """

    def __init__(self):
        self.locked_counter = 0
        self.current_turn = 0
        self.nb_players = 4
        self.players = []
        self.table = []

        self.np_random = None
        self.action_space = spaces.Discrete(28)
        self.observation_space = spaces.Tuple((spaces.Discrete(3),) * 28)

        self.seed()
        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action: int):
        assert self.action_space.contains(action)

        current_hand = self.players[self.current_turn]

        assert valid_move(self.table, hand=current_hand, indice=action) is True

        if action is not None:
            # hit: add a tile to table and reset locked_counter
            self.table.insert(
                index=insert_index(self.table, action), object=current_hand.pop(action)
            )
            self.locked_counter = 0

        else:
            # stick: inc the locked_counter, until nb_players is reached
            self.locked_counter += 1

        if len(current_hand) <= 0:
            # done: (neat) win by playing
            done = True
            reward = 1

        elif self.locked_counter >= self.nb_players:
            # done: (cheat) win by scoring
            done = True
            reward = 0

        else:
            done = False
            reward = 0

        self.current_turn += 1

        return self._get_obs(), reward, done, {}

    def reset(self):
        self.locked_counter = 0
        self.current_turn = 0
        self.players = []
        self.table = []

        game_pack = [_domino_to_indice(domino) for domino in pack]
        hand_size = len(game_pack) // self.nb_players

        self.np_random.shuffle(game_pack)

        for i in range(0, len(game_pack), hand_size):
            self.players.append(game_pack[i : i + hand_size])

        return self._get_obs()

    def render(self, mode="human"):
        if mode == "human":
            output = ""

            table = [_indice_to_domino(indice) for indice in self.table]
            output += "Table: %s\n" % table

            for i, hand in enumerate(self.players):
                hand = [_indice_to_domino(indice) for indice in hand]
                output += "Player %s: %s\n" % (i, hand)

            print(output)

    def _get_obs(self):
        table = self.table
        current_hand = self.players[self.current_turn]

        observation = []
        for domino in pack:
            indice = _domino_to_indice(domino)
            if indice in table:
                observation.append(2)
            elif indice in current_hand:
                observation.append(1)
            else:
                observation.append(0)
        return observation
