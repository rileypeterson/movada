from absl import app
from absl import flags

import bsuite
from bsuite import sweep

from bsuite.baselines import experiment
from bsuite.baselines.tf import dqn, actor_critic
from bsuite.baselines.utils import pool

import sonnet as snt

# Internal imports.

# Experiment flags.
flags.DEFINE_string(
    "bsuite_id",
    "kelly/3",
    "BSuite identifier. "
    "This global flag can be used to control which environment is loaded.",
)
flags.DEFINE_string("save_path", "/tmp/bsuite", "where to save bsuite results")
flags.DEFINE_enum(
    "logging_mode",
    "terminal",
    ["csv", "sqlite", "terminal"],
    "which form of logging to use for bsuite results",
)
flags.DEFINE_boolean("overwrite", False, "overwrite csv logging if found")
flags.DEFINE_integer("num_episodes", None, "Overrides number of training eps.")

flags.DEFINE_integer("num_hidden_layers", 2, "number of hidden layers")
flags.DEFINE_integer("num_units", 50, "number of units per hidden layer")
flags.DEFINE_integer("batch_size", 32, "size of batches sampled from replay")
flags.DEFINE_float("discount", 1.0, "discounting on the agent side")
flags.DEFINE_integer("replay_capacity", 100000, "size of the replay buffer")
flags.DEFINE_integer("min_replay_size", 128, "min replay size before training.")
flags.DEFINE_integer("sgd_period", 1, "steps between online net updates")
flags.DEFINE_integer("target_update_period", 4, "steps between target net updates")
flags.DEFINE_float("learning_rate", 1e-4, "learning rate for optimizer")
flags.DEFINE_float("epsilon", 0.05, "fraction of exploratory random actions")
flags.DEFINE_integer("seed", 42, "seed for random number generation")
flags.DEFINE_boolean("verbose", True, "whether to log to std output")
flags.DEFINE_integer("sequence_length", 32, "mumber of transitions to batch")
flags.DEFINE_float("td_lambda", 0.9, "mixing parameter for boostrapping")


FLAGS = flags.FLAGS


def run(bsuite_id: str) -> str:
    """Runs a DQN agent on a given bsuite environment, logging to terminal."""

    env = bsuite.load_and_record(
        bsuite_id=bsuite_id,
        save_path=FLAGS.save_path,
        logging_mode=FLAGS.logging_mode,
        overwrite=FLAGS.overwrite,
    )

    # Making the networks.
    hidden_units = [FLAGS.num_units] * FLAGS.num_hidden_layers
    network = snt.Sequential(
        [
            snt.Flatten(),
            snt.nets.MLP(hidden_units + [env.action_spec().num_values]),
        ]
    )
    optimizer = snt.optimizers.Adam(learning_rate=FLAGS.learning_rate)

    agent = dqn.DQN(
        action_spec=env.action_spec(),
        network=network,
        batch_size=FLAGS.batch_size,
        discount=FLAGS.discount,
        replay_capacity=FLAGS.replay_capacity,
        min_replay_size=FLAGS.min_replay_size,
        sgd_period=FLAGS.sgd_period,
        target_update_period=FLAGS.target_update_period,
        optimizer=optimizer,
        epsilon=FLAGS.epsilon,
        seed=FLAGS.seed,
    )

    num_episodes = FLAGS.num_episodes or getattr(env, "bsuite_num_episodes")
    experiment.run(
        agent=agent, environment=env, num_episodes=num_episodes, verbose=FLAGS.verbose
    )

    # hidden_sizes = [FLAGS.num_units] * FLAGS.num_hidden_layers
    # network = actor_critic.PolicyValueNet(
    #     hidden_sizes=hidden_sizes,
    #     action_spec=env.action_spec(),
    # )
    # agent = actor_critic.ActorCritic(
    #     obs_spec=env.observation_spec(),
    #     action_spec=env.action_spec(),
    #     network=network,
    #     optimizer=snt.optimizers.Adam(learning_rate=FLAGS.learning_rate),
    #     max_sequence_length=FLAGS.sequence_length,
    #     td_lambda=FLAGS.td_lambda,
    #     discount=FLAGS.discount,
    #     seed=FLAGS.seed,
    # )
    #
    # num_episodes = FLAGS.num_episodes or getattr(env, "bsuite_num_episodes")
    # experiment.run(
    #     agent=agent, environment=env, num_episodes=num_episodes, verbose=FLAGS.verbose
    # )

    return bsuite_id


def main(argv):
    # Parses whether to run a single bsuite_id, or multiprocess sweep.
    del argv  # Unused.
    bsuite_id = FLAGS.bsuite_id

    if bsuite_id in sweep.SWEEP:
        print(f"Running single experiment: bsuite_id={bsuite_id}.")
        run(bsuite_id)

    elif hasattr(sweep, bsuite_id):
        bsuite_sweep = getattr(sweep, bsuite_id)
        print(f"Running sweep over bsuite_id in sweep.{bsuite_sweep}")
        FLAGS.verbose = False
        pool.map_mpi(run, bsuite_sweep)

    else:
        raise ValueError(f"Invalid flag: bsuite_id={bsuite_id}.")


if __name__ == "__main__":
    app.run(main)
