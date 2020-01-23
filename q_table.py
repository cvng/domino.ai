import sqlite3

from domino import pack

DB = sqlite3.connect("q_table.db")

action_space_n = len(pack) * 2 + 1

action_columns = ", ".join([f"action_{action}" for action in range(action_space_n + 1)])


def create_q_values_table():
    global action_columns
    action_columns = ", ".join(
        [f"{action} REAL NOT NULL DEFAULT 0.0" for action in action_columns.split(", ")]
    )

    with DB:
        DB.execute(
            """
            DROP TABLE IF EXISTS q_values;
            """
        )
        DB.execute(
            f"""
            CREATE TABLE IF NOT EXISTS q_values (observation INTEGER PRIMARY KEY NOT NULL, {action_columns});
            """
        )
    return True


def insert_q_value(observation, action, q_value):
    if not q_value:
        return False
    with DB:
        result = DB.execute(
            f"""
            UPDATE q_values SET action_{action} = {q_value} WHERE observation = {observation};
            """
        )
    if result.rowcount < 1:
        with DB:
            DB.execute(
                f"""
                INSERT INTO q_values (observation, action_{action}) VALUES ({observation}, {q_value});
                """
            )
    return True


def select_q_values_table():
    with DB:
        result = DB.execute(
            """
            SELECT * FROM q_values;
            """
        ).fetchall()
    if result:
        return result


def select_q_value(observation, action):
    with DB:
        result = DB.execute(
            f"""
            SELECT action_{action} FROM q_values WHERE observation = {observation};
            """
        ).fetchone()
    if result and result[0]:
        return result[0]


def select_max_q_value(observation):
    with DB:
        result = DB.execute(
            f"""
            SELECT {action_columns} FROM q_values WHERE observation = {observation};
            """
        ).fetchone()
    if result:
        return max(result)


def select_max_action(observation):
    with DB:
        result = DB.execute(
            f"""
            SELECT {action_columns} FROM q_values WHERE observation = {observation};
            """
        ).fetchone()
    if result:
        return result.index(max(result))


if __name__ == "__main__":
    create_q_values_table()
