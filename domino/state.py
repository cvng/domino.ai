from random import shuffle
from typing import List, Tuple

from .constants import State, Player, Domino
from .strategies import random_picker

default_strategy = random_picker


initial_state: State = {
    "players": {},
    "table": [],
    "history": [],
    "winner": None,
    "last_pop": None,
    "last_move": None,
}

state: State = {}

"""MUTATORS (update state)"""

# Game


def game_init() -> State:
    global initial_state, state
    state = initial_state.copy()
    return state


def game_update_history(play: tuple) -> State:
    global state
    state["history"].append(play)
    return state


# Table


def table_init(dominoes: List[Domino]) -> State:
    global state
    state["table"] = dominoes
    return state


def table_shuffle() -> State:
    global state
    shuffle(state["table"])
    return state


def table_pop() -> State:
    global state
    state["last_pop"] = state["table"].pop()
    return state


def table_insert(index_to_insert: int, domino_to_play: Domino) -> State:
    global state
    if index_to_insert == -1:
        index_to_insert = len(state["table"])
    state["table"].insert(index_to_insert, domino_to_play)
    return state


# Player


def player_init(player_id: int, strategy: callable) -> State:
    global state
    player = {"id": player_id, "hand": [], "strategy": strategy or default_strategy}
    state["players"][player_id] = player
    return state


def player_pick(player_id: int) -> State:
    global state

    domino = table_pop() and get_last_pop()

    state["players"][player_id]["hand"].append(domino)
    return state


def player_pop(player_id: int, index: int) -> State:
    global state

    state["players"][player_id]["hand"].pop(index)

    return state


def player_play(player_id: int) -> State:
    global state

    table = get_table()
    player = get_player(player_id)

    result = player["strategy"](table, player["hand"])
    if result:
        domino, i = result
        try:
            player_pop(player_id, player["hand"].index(domino))
        except ValueError:
            player_pop(player_id, player["hand"].index(domino[::-1]))

        state["last_move"] = domino, i
    else:
        state["last_move"] = None

    game_update_history((player["id"], result))

    return state


"""SELECTORS (read state)"""


# Game


def get_table() -> List[Domino]:
    global state
    return state["table"]


def get_last_pop() -> Domino:
    global state
    return state["last_pop"]


def get_last_move() -> Tuple[Domino, int]:
    global state
    return state["last_move"]


# Player


def player_add(player_id: int, player: Player) -> State:
    global state
    state["players"][player_id] = player
    return state


def set_winner(winner: Player) -> State:
    global state
    state["winner"] = winner
    return state


def get_players() -> List[Player]:
    global state
    return list(state["players"].values())


def get_player(player_id: int) -> Player:
    return state["players"][player_id]


def get_player_hand(player_id: int) -> List[Domino]:
    return get_player(player_id)["hand"]


def get_player_total(player_id: int) -> int:
    player = get_player(player_id)
    return sum([item for sublist in player["hand"] for item in sublist])


def get_winner() -> Player:
    global state
    return state["winner"]


def get_winner_total() -> int:
    global state
    winner = get_winner()
    return get_player_total(winner["id"])


def get_player_repr(player_id: int) -> str:
    player = get_player(player_id)
    return "<Player #%s: %s>" % (player["id"], player["hand"])


def get_player_strategy(player_id: int) -> callable:
    player = get_player(player_id)
    return player["strategy"]


def get_ranking() -> List[Player]:
    return sorted(get_players(), key=lambda p: get_player_total(p["id"]))
