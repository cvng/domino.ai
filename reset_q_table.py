import argparse
import logging

from agents.utils.q_table import DB, create_q_values_table

logger = logging.getLogger(__name__)

logging.basicConfig(level="INFO")


def reset_q_table(force=True):
    DB.set_trace_callback(logger.info)

    result = create_q_values_table(drop_if_exists=force)

    logger.info("OK! result=%s" % result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", default=True)
    args = parser.parse_args()
    reset_q_table(**vars(args))
