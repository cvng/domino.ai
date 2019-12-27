from random import randrange

from .constants import FIRST_PLAY


def basic_strategy(strategy: callable) -> callable:
    def fn(state, choices):
        # first play
        if len(state) == 0:
            if FIRST_PLAY not in choices:
                return
            return FIRST_PLAY, 0

        # regular play
        result = strategy(state, choices)

        if not result:
            return
        choice_index, i = result
        choice = choices[choice_index]
        if state and i == 0 and choice[1] != state[0][0]:
            choice = choice[::-1]
        elif state and i == -1 and choice[0] != state[-1][1]:
            choice = choice[::-1]
        return choice, i

    return fn


@basic_strategy
def naive_ltr(state: list, choices: list) -> tuple:
    """
    Naive LTR strategy.
    """
    left_n = state[0][0]
    right_n = state[-1][1]

    for i, choice in enumerate(choices):
        if left_n in choice:
            return i, 0
        elif right_n in choice:
            return i, -1


@basic_strategy
def random_picker(state: list, choices: list) -> tuple:
    """
    Random Picker strategy.
    """
    left_n = state[0][0]
    right_n = state[-1][1]

    possibilities = []

    for i, choice in enumerate(choices):
        if left_n in choice:
            possibilities.append((i, 0))
        elif right_n in choice:
            possibilities.append((i, -1))

    if len(possibilities):
        return possibilities.pop(randrange(len(possibilities)))


tested_strategy = naive_ltr
