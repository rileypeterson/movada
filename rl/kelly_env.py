from bsuite.environments import base
from bsuite.experiments.kelly import sweep
from scipy.stats import mode

import dm_env
from dm_env import specs
import numpy as np

# Fraction of your capital you can wager
_ACTIONS = tuple(range(101))  # Left, no-op, right.


class Kelly(base.Environment):
    """A Catch environment built on the dm_env.Environment class.

    The agent must move a paddle to intercept falling balls. Falling balls only
    move downwards on the column they are in.

    The observation is an array shape (rows, columns), with binary values:
    zero if a space is empty; 1 if it contains the paddle or a ball.

    The actions are discrete, and by default there are three available:
    stay, move left, and move right.

    The episode terminates when the ball reaches the bottom of the screen.
    """

    def __init__(self, p_win=0.55, start_balance=100, seed=None):
        """Initializes a new Catch environment.

        Args:
          rows: number of rows.
          columns: number of columns.
          seed: random seed for the RNG.
        """
        self._p_win = p_win
        self._start_balance = start_balance
        self._balance = None
        self._reset_next_step = True
        self._rng = np.random.RandomState(seed)
        self._rand = None
        self.bsuite_num_episodes = sweep.NUM_EPISODES
        self._chosen_actions = []

    def _reset(self) -> dm_env.TimeStep:
        """Returns the first `TimeStep` of a new episode."""
        self._reset_next_step = False
        self._balance = self._start_balance
        return dm_env.restart(self._observation())

    def _step(self, action: int) -> dm_env.TimeStep:
        """Updates the environment according to the action."""
        if self._reset_next_step:
            return self.reset()

        # Attempt
        # f = _ACTIONS[action] / 100.0
        # for _ in range(5):
        #     self._chosen_action = f
        #     bet_amount = f * self._balance
        #     self._balance -= bet_amount
        #     rand = self._observation()
        #     if rand[0] < self._p_win:
        #         # We won!
        #         self._balance += 2 * (bet_amount)
        # # self._reset_next_step = True
        # return dm_env.termination(reward=self._balance - self._start_balance, observation=rand)

        # Move the paddle.
        f = _ACTIONS[action] / 100.0
        while len(self._chosen_actions) > 100:
            self._chosen_actions.pop(0)
        self._chosen_actions.append(f)

        k = 0
        mul = 10
        while (0.000001 < self._balance <= mul * self._start_balance) and k < 1000:
            ran = self._rng.random()
            # print(self._balance, f, ran)
            bet_amount = f * self._balance
            self._balance -= bet_amount
            if ran < self._p_win:
                # We won!
                self._balance += 2 * (bet_amount)
            k += 1

        # Stop when we reach 2 * self._start_balance or 0.0
        self._reset_next_step = True
        if self._balance >= mul * self._start_balance:
            # print(k, f)
            return dm_env.termination(reward=1, observation=self._observation())
        elif self._balance <= 0.000001:
            return dm_env.termination(reward=-1, observation=self._observation())
        return dm_env.termination(reward=0, observation=self._observation())

    def observation_spec(self) -> specs.BoundedArray:
        """Returns the observation spec."""
        return specs.BoundedArray(
            shape=(1,), dtype=np.float32, name="board", minimum=0, maximum=1
        )

    def action_spec(self) -> specs.DiscreteArray:
        """Returns the action spec."""
        return specs.DiscreteArray(
            dtype=np.int, num_values=len(_ACTIONS), name="action"
        )

    def _observation(self) -> np.ndarray:
        self._rand = np.array([self._rng.random()], dtype=np.float32)
        return self._rand

    def bsuite_info(self):
        return dict(chosen_actions=mode(self._chosen_actions), balance=self._balance)
