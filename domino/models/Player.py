from ..strategies import random_picker
from ..utils import flatten

default_strategy = random_picker


class Player:
    def __init__(self, player_id, strategy=None):
        self.id = player_id
        self.hand = []
        self.strategy = strategy or default_strategy

    def __repr__(self):
        return f"<Player #{self.id}: {self.hand}>"

    def play(self, table):
        result = self.strategy(table, self.hand)
        if result:
            domino, i = result
            try:
                self.hand.pop(self.hand.index(domino))
            except ValueError:
                self.hand.pop(self.hand.index(domino[::-1]))
            return domino, i

    def pick(self, domino):
        self.hand.append(domino)

    @property
    def total(self):
        return sum(flatten(self.hand))
