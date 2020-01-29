import argparse

from agents.utils.q_table import DB, create_q_values_table


def reset_q_table(force=True):
    print("Creating q_values table.")

    DB.set_trace_callback(lambda x: print(x.strip()))

    create_q_values_table(drop_if_exists=force)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", default=True)
    args = parser.parse_args()
    reset_q_table(**vars(args))
