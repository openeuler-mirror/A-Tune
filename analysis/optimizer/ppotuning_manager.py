# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2022-11-25
"""
This class is used to perform Proximal Policy Optimization algorithm tuning and
generate optimized profile.
"""

import logging
from typing import Tuple
import numpy as np
import gym
import torch
from stable_baselines3 import PPO

LOGGER = logging.getLogger(__name__)


class Knobs():
    """
    Class to parse knobs and create action space for RL-algorithm
    """

    def __init__(self, knobs) -> None:
        self.knobs = knobs

    def create_action_space(self) -> Tuple[dict, np.ndarray, gym.Space]:
        """Function builds action space and useful data about action

        Returns:
            Union[dict, np.ndarray, gym.Space]: Dictionary with knobs values,
            upper-limits and action-space
        """
        knob_dict = {}
        knob_upper_limit = []
        space_size = []
        for knob in self.knobs:
            if knob.get('dtype') == 'int':
                lower_limit = knob.get('range')[0]
                upper_limit = knob.get('range')[1]
                step_size = knob.get('step')
                if step_size > 0:
                    vals = list(range(lower_limit, upper_limit+1, step_size))
                else:
                    num = np.minimum(32, upper_limit-lower_limit+1)
                    vals = np.linspace(lower_limit, upper_limit, num,
                                       dtype=np.int32).tolist()
            elif knob.get('dtype') == 'string':
                vals = knob.get('options')
                upper_limit = len(vals)-1

            knob_dict[knob.get('name')] = {'vals': vals, 'length': len(vals)}
            space_size.append(len(vals))
            knob_upper_limit.append(upper_limit)

        return knob_dict, \
            np.array(knob_upper_limit, dtype=np.float32), \
            gym.spaces.MultiDiscrete(space_size)


class KnobEnv(gym.Env):
    """
    Environment for RL algorithm
    """

    def __init__(self, knobs: Knobs, child_conn) -> None:
        super().__init__()
        self.knob_dict, self.knob_upper_limit, self.action_space = knobs.create_action_space()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(
            len(self.knob_upper_limit),), dtype=np.float32)
        self.best_params = {}
        self.best_reward = 0
        self._child_conn = child_conn

    def step(self, action):
        param = self._action_to_params(action)
        self._child_conn.send(param)
        result = self._child_conn.recv()
        reward = 0.0
        eval_list = result.split(',')
        for value in eval_list:
            reward += -1.0*float(value)

        if reward > self.best_reward:
            self.best_reward = reward
            self.best_params = param

        state = action/self.knob_upper_limit

        return state, np.log10(reward), False, {}

    def reset(self):
        return self.action_space.sample()

    def _action_to_params(self, action):
        params = {}
        for i, act in enumerate(action):
            param_name = list(self.knob_dict.keys())[i]
            param_value = self.knob_dict.get(param_name).get('vals')[act]
            params[param_name] = param_value
        return {'param': params}

    def render(self, mode=''):
        pass


class PPOOptimizer:
    """
    Proximal policy optimization
    """

    def __init__(self, knobs, child_conn, max_eval) -> None:
        self._child_conn = child_conn
        self._max_eval = max_eval
        self._knobs = knobs

    def run(self) -> dict[str, dict]:
        """Run optimization with PPO

        Returns:
            dict[str, dict]: best parameters of the tuned system
        """
        knobs = Knobs(self._knobs)
        env = KnobEnv(knobs, self._child_conn)
        policy_kwargs = dict(activation_fn=torch.nn.ReLU)
        model = PPO('MlpPolicy',
                    env,
                    verbose=0,
                    n_epochs=4,
                    policy_kwargs=policy_kwargs,
                    learning_rate=5e-4,
                    device='cpu',
                    n_steps=5,
                    batch_size=5,
                    gamma=0.1
                    )
        model.learn(self._max_eval)

        return env.best_params

