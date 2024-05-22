# ACRLF_env.py
# creates new environment ACRLF
# 
# Copyright (c) 2023 Advanced Micro Devices Inc.
# Report Bugs to Shamith Achanta <Shamith.Achanta@amd.com>
#

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import subprocess
import time
import os
import sys
# import torch
from datetime import datetime

home = os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging')
sys.path.insert(0, os.path.join(home, 'ACRLF'))
import _ACRLF

sys.path.insert(0, os.path.join(home, 'scripts'))
from collect_data import *
from battery_functions import *

class ACRLF(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        # state size
        self.size = 5
        # bounds for state space
        lower_bnds = np.zeros(shape=(self.size,))
        upper_bnds = np.array([45, 100, collect_data(batt_cap=1), 180, 100])
        # state space: 5; discrete
        self.observation_space = spaces.Box(lower_bnds, upper_bnds, dtype=np.uint64)

        self.observation = None

        self.action_list = np.array([1, 20, 40, 60, 80, 100])
        self.action_space = spaces.Discrete(len(self.action_list))

        # Hyperparameters
        self.T_L = 10
        self.T_H = 35
        self.S_L = 40
        self.S_H = 70
        self._alpha = [1, 2, 10]
        self._beta = [4, 4]
        self._gamma = 6
        self._omega = [0.25, 0.5, 1.0]

        self.S_max = 95
        self.T_max = [0, 45]
            

    def step(self, action):
        terminated = False
        truncated = False
        info = {}
        T = [0, 0]
        
        # inputs to reward function
        T[0] = self.observation[0]
        S_prime = self.observation[1]

        if S_prime >= self.S_max or self.observation[4] <= 0 or T[0] <= self.T_max[0] or T[0] >= self.T_max[1]:
            terminated = True

        # change battery charging rate (action for agent 2)
        if terminated == False and truncated == False:
            retVal = batteryTempandRate(1, action)
        
            if retVal != 0:
                truncated = True

            # wait for charging rate to change and update battery parameters
            time.sleep(2)
        
        # next state
        next_state = np.array(collect_data(agent=2, batt_cap=0), np.uint64)
        self.observation = next_state
        
        # battery temperature
        T[1] = next_state[0]

        if next_state[1] >= self.S_max or T[1] <= self.T_max[0] or T[1] >= self.T_max[1]:
            terminated = True

        # calculate reward
        reward = self.reward_function(action, T, S_prime)

        # check to see if episode has to end
        if terminated or truncated:
            self.endEpisode()
        
        return next_state, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        if not os.path.exists(os.path.join(home, '.done')): 
            info = {}
            self.observation = np.array(collect_data(agent=2, battery=0), np.uint64)
            return self.observation, info
        
        else:
            sys.exit()
    
    def render(self, mode="human"):
        pass

    def close(self):
        pass
    
    def startEpisode(self):
        os.remove(os.path.join(home, '.done'))
    
    def endEpisode(self):
        with open(os.path.join(home, '.done'), 'w+') as _:
            pass
    
    def saveObservation(self, observation):
        self.observation = observation
    
    def reward_function(self, I: int, T: list, S_prime: int):
        T_prime = T[1]
        delta_T = T_prime - T[0]

        if T_prime < self.T_L:
            return -np.inf
        elif T_prime > self.T_H:
            return -np.inf

        if T_prime < self.T_L and S_prime <= self.S_L:
            reward = - (T_prime - self.T_L) * delta_T * _alpha[0] * _omega[0] + I * (self.S_L - S_prime) * _beta[0]
        elif (T_prime >= self.T_L and T_prime <= self.T_H) and S_prime <= self.S_L:
            reward = - delta_T * _alpha[1] * _omega[0] + I * (self.S_L - S_prime) * _beta[0]
        elif T_prime > self.T_H and S_prime <= self.S_L:
            reward = - (T_prime - self.T_H) * delta_T * _alpha[2] * _omega[0] + I * (self.S_L - S_prime) * _beta[0]

        elif T_prime < self.T_L and (S_prime > self.S_L and S_prime <= self.S_H):
            reward = - (T_prime - self.T_L) * delta_T * _alpha[0] * _omega[1] + 0
        elif (T_prime >= self.T_L and T_prime <= self.T_H) and (S_prime > self.S_L and S_prime <= self.S_H):
            reward = - delta_T * _alpha[1] * _omega[1] + 0
        elif T_prime > self.T_H and S_prime <= (S_prime > self.S_L and S_prime <= self.S_H):
            reward = - (T_prime - self.T_H) * delta_T * _alpha[2] * _omega[1] + 0
        
        elif T_prime < self.T_L and S_prime > self.S_H:
            reward = - (T_prime - self.T_L) * delta_T * _alpha[0] * _omega[2] + (1.0 * _beta[1]) / (I * (S_prime - self.S_H))
        elif (T_prime >= self.T_L and T_prime <= self.T_H) and S_prime > self.S_H:
            reward = - delta_T * _alpha[1] * _omega[2] + (1.0 * _beta[1]) / (I * (S_prime - self.S_H))
        elif T_prime > self.T_H and S_prime > self.S_H:
            reward = - (T_prime - self.T_H) * delta_T * _alpha[2] * _omega[2] + (1.0 * _beta[1]) / (I * (S_prime - self.S_H))
        else:
            pass
        
        return reward   

    
# test function
def test(env):
    env = gym.make('ACRLF-v0')

    observation, info = env.reset()
    
    for _ in range(10):
        action = env.action_space.sample()
        # action = Agent2(observation)

        observation, reward, terminated, truncated, info = env.step(action)

        print(observation, reward, terminated, truncated)

        if terminated or truncated:
            observation, info = env.reset()
    
    env.close()

if __name__ == '__main__':
    test(ACRLF())
