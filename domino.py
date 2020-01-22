"""
Author: Cedric Vangout <mail@cvng.dev>
Gym Environment: cvng/Domino-v0
Permalink: https://github.com/cvng/domino.ai
"""

from typing import Optional, List, Tuple

import gym
import numpy as np
from gym import spaces
from gym.utils import seeding

Domino = Tuple[int, int]

pack: List[Domino] = [
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


def valid_move(
    table: List[Domino], hand: List[Domino], domino: Optional[Domino]
) -> bool:
    """
    >>> valid_move([(0, 0)], [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 1)], (0, 0))
    False
    >>> valid_move([(0, 0)], [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 1)], (1, 2))
    False
    >>> valid_move([], [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 1)], (0, 1))
    False
    >>> valid_move([(0, 0)], [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 1)], (1, 1))
    False
    >>> valid_move([], [(0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 1)], (0, 0))
    True
    """

    # domino should be played if possible
    if not domino:
        if possibilities(table, hand):
            return False
        else:
            return True

    # domino already played
    if domino in table or domino[::-1] in table:
        return False

    # domino not in hand
    if not (domino in hand or domino[::-1] in hand):
        return False

    # domino to be played first is (0, 0) aka pack[0]
    if len(table) == 0 and domino != pack[0]:
        return False

    # domino do not match what is on table
    if insert_index(table, domino) is None:
        return False

    return True


def insert_index(table: List[Domino], domino: Domino) -> Optional[Tuple[int, Domino]]:
    """
    >>> insert_index([], (0, 0))
    (0, (0, 0))
    >>> insert_index([(0, 0)], (0, 1))
    (0, (1, 0))
    >>> insert_index([(0, 0), (0, 1)], (2, 1))
    (2, (1, 2))
    >>> insert_index([(0, 0)], (1, 1)) is None
    True
    """
    if len(table) == 0:
        return 0, domino

    first_domino = table[0]
    last_domino = table[-1]

    if first_domino[0] == domino[0]:
        return 0, domino[::-1]

    elif last_domino[1] == domino[0]:
        return len(table), domino

    elif first_domino[0] == domino[1]:
        return 0, domino

    elif last_domino[1] == domino[1]:
        return len(table), domino[::-1]

    return None


def possibilities(table: List[Domino], hand: List[Domino]) -> List[Domino]:
    """
    >>> possibilities([(4, 0), (0, 0), (0, 2)], [(3, 4), (2, 5), (4, 4), (2, 6), (1, 3), (3, 5), (0, 5)])
    [(3, 4), (2, 5), (4, 4), (2, 6)]
    """
    return [domino for domino in hand if valid_move(table, hand, domino)]


def dtoa(domino: Domino, pack_size: int = len(pack)) -> int:
    """
    >>> dtoa((0,0))
    1
    >>> dtoa((0, 1))
    2
    >>> dtoa((1, 0), pack_size=28)
    30
    """
    try:
        return pack.index(domino) + 1  # domino to action
    except ValueError:
        return pack.index(domino[::-1]) + pack_size + 1


def atod(action: int, pack_size: int = len(pack)) -> Optional[Domino]:
    """
    >>> atod(1)
    (0, 0)
    >>> atod(2)
    (0, 1)
    >>> atod(30, pack_size=28)
    (1, 0)
    """
    if action == 0:
        return None
    domino = pack[action % pack_size - 1]
    if action > pack_size:
        domino = domino[::-1]
    return domino  # action to domino


class DominoEnv(gym.Env):
    """Simple domino environment

    Dominoes is a family of tile-based games played with rectangular "domino" tiles.

    Each domino is a rectangular tile with a line dividing its face into two square ends.
    Each end is marked with a number of spots (also called pips, nips, or dobs) or is blank.
    The backs of the dominoes in a set are indistinguishable, either blank or having some common design.

    The domino gaming pieces make up a domino set, sometimes called a deck or pack.
    The traditional Sino-European domino set consists of 28 dominoes,
    featuring all combinations of spot counts between zero and six.

    Action meaning:
        0 = skip turn (NOOP)
        1-28 = play tile

    Observation meaning (unraveled):
        [0:27] -> 3 possible values:
        0 = not seen (not in current_hand + not in table)
        1 = in current_hand
        2 = in table
        [28] -> 7 possible values:
        0-6 = leftmost number in table
        [29] -> 7 possible values:
        1-6 = rightmost number in table
    """

    def __init__(self):
        self.locked_counter = 0
        self.current_turn = 0
        self.n_players = 4
        self.players = []
        self.table = []

        self.np_random = None
        self.action_space = spaces.Discrete(len(pack) * 2 + 1)
        self.observation_space = spaces.Discrete(1120962830293088)  # FIXME: compute n

        self.seed(0)  # FIXME: remove seed
        self.reset()

    def seed(self, seed: int = None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action: int):
        from agents import RandomAgent

        assert self.current_turn == 0
        observation, reward, done, info = self._play(action)

        if not done:
            for player in range(1, self.n_players):
                agent = RandomAgent(self.action_space, self.np_random)
                action = agent.act(observation, reward, done)

                assert self.current_turn == player
                observation, reward, done, info = self._play(action)

                if done:
                    break

        return observation, reward, done, info

    def _play(self, action: int):
        assert self.action_space.contains(action)

        domino = atod(action)

        current_hand = self.players[self.current_turn]

        assert valid_move(self.table, hand=current_hand, domino=domino) is True

        if domino:
            # hit: add a tile to table and reset locked_counter
            self.locked_counter = 0
            try:
                current_hand.pop(current_hand.index(domino))
            except ValueError:
                current_hand.pop(current_hand.index(domino[::-1]))
            index_to_insert, domino_to_play = insert_index(
                table=self.table, domino=domino
            )
            self.table.insert(index_to_insert, domino_to_play)

        else:
            # stick: inc the locked_counter, until n_players is reached
            self.locked_counter += 1

        if len(current_hand) <= 0:
            # done: (neat) win by playing
            done = True
            reward = 1 if self.current_turn == 0 else -1

        elif self.locked_counter >= self.n_players:
            # done: (cheat) win by scoring
            done = True
            reward = -1

        else:
            done = False
            reward = 0

        self.current_turn = (self.current_turn + 1) % self.n_players

        return self._get_obs(), reward, done, {}

    def reset(self):
        self.locked_counter = 0
        self.current_turn = 0
        self.players = []
        self.table = []

        game_pack = [domino for domino in pack]
        hand_size = len(game_pack) // self.n_players

        self.np_random.shuffle(game_pack)

        for i in range(0, len(game_pack), hand_size):
            self.players.append(game_pack[i : i + hand_size])

        assert all(len(player) == hand_size for player in self.players)

        return self._get_obs()

    def render(self, mode: str = "human"):
        if mode == "human":
            output = ""

            output += "Table: %s\n" % self.table

            for i, hand in enumerate(self.players):
                current = "<-" if self.current_turn == i else ""
                output += "Player %s: %s %s\n" % (i, hand, current)

            output += "locked_counter: %s\n" % self.locked_counter

            print(output)

    def _get_obs(self):
        observation = []

        table = self.table
        current_hand = self.players[self.current_turn]

        for domino in pack:
            if domino in table or domino[::-1] in table:
                observation.append(2)

            elif domino in current_hand or domino[::-1] in current_hand:
                observation.append(1)

            else:
                observation.append(0)

        if table:
            leftmost_n, rightmost_n = table[0][0], table[-1][1]
            observation += [leftmost_n, rightmost_n]
        else:
            observation += [0, 0]

        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel_multi_index.html
        observation = np.ravel_multi_index(observation, dims=(*(3,) * len(pack), 7, 7))

        return int(observation)
