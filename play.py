import argparse

import gym

from agents.ql import QLAgent

ENV_NAME = "Domino-v0"


def play(episodes=3000, debug=False):
    # Get the environment.
    env = gym.make(ENV_NAME)

    # Configure our agent.
    agent = QLAgent()

    # Learn something!
    agent.fit(env, nb_steps=episodes * 15, visualize=debug, verbose=2)

    # Evaluate our algorithm for 5 episodes.
    agent.test(env, nb_episodes=5, visualize=debug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episodes", type=int, nargs="?")
    args = parser.parse_args()
    play(*[arg for arg in vars(args).values() if arg])
