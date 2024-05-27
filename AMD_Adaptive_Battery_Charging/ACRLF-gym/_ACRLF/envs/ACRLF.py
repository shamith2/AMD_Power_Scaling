# ACRLF_env.py
# creates new environment ACRLF
#

import gym
from gym import spaces
import numpy as np
import subprocess
import time
import os
import sys
from datetime import datetime
import multiprocessing

home = os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging')
sys.path.insert(0, os.path.join(home, 'ACRLF-gym'))
import _ACRLF

sys.path.insert(0, os.path.join(home, 'SCRIPTS'))
from collect_data import *
from battery_functions import *
from pipe import *

sys.path.insert(0, os.path.join(home, 'GUI'))
from gui import *

class ACRLF(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, t_optimal: int, S_prime: int, _delta: float = 1.0):
        super(ACRLF, self).__init__()

        # state size
        self.size = 5
        
        # bounds for state space
        self.battery_capacity, self.design_capacity = collect_data(agent=0, battery=1, store=False) # mAh
        lower_bnds = np.zeros(shape=(self.size,))
        upper_bnds = np.array([45, 100, self.design_capacity, 180, 100])
        
        # state space: 5; discrete
        self.observation_space = spaces.Box(lower_bnds, upper_bnds, dtype=np.uint64)
        self.observation = None

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

        # Charging Current / Rate: # 0xFFFC := 65532, 0xFFFF := 65535
        df = pd.read_csv(os.path.join(home, 'DATASETS', 'charge_history.csv'))
        if S_prime < 85:
            entry = df.loc[(df['Charge Rate Input'] == 65535) & (df['State of Charge'] == 45)]
        else:
            entry = df.loc[(df['Charge Rate Input'] == 65535) & (df['State of Charge'] == 90)]

        self.I_system = entry['Charge Rate Output (mW)'].iloc[0] # mW
        self.voltage = entry['Battery Voltage (mV)'].iloc[0] # self.collect_data(agent=0, battery=0)[-3] # mV

        # action space       
        if S_prime > 0 and S_prime <= self.S_L:
            self.action_list = np.floor(np.multiply(np.array([0.6, 0.7, 0.8, 0.9]), self.I_system)).astype(np.uint64)
        elif S_prime > self.S_H and S_prime <= 100:
            self.action_list = np.floor(np.multiply(np.array([0.1, 0.2, 0.3, 0.4, 0.5]), self.I_system)).astype(np.uint64)
        else:
            self.action_list = np.array([min(np.floor((self.battery_capacity * ((self.S_H - S_prime) / 100)) / (_delta * (t_optimal / 60))).astype(np.uint64), self.I_system)])
        
        print(self.battery_capacity, np.floor((self.battery_capacity * ((self.S_H - S_prime) / 100)) / (_delta * (t_optimal / 60))).astype(np.uint64))
        print(self.action_list, self.design_capacity)

        

        gg

        self.action_space = spaces.Discrete(len(self.action_list))
            

    def step(self, action):
        terminated = False
        truncated = False
        info = {}
        T = [0, 0]
        
        # inputs to reward function
        T[0] = self.observation[0]
        S_prime = self.observation[1]

        # boundary checks
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
        next_state = self.collect_data(agent=2, battery=0, store=False)
        
        # battery temperature
        T[1] = next_state[0]

        # boundary checks
        if next_state[1] >= self.S_max or T[1] <= self.T_max[0] or T[1] >= self.T_max[1]:
            terminated = True

        # calculate reward
        reward = self.reward_function(action, T, S_prime)

        # check to see if episode has to end
        if terminated or truncated:
            self.endEpisode()
        
        return next_state, reward, terminated or truncated, info

    def reset(self):
        if not os.path.exists(os.path.join(home, '.done')):
            return self.collect_data(agent=2, battery=0, store=False)
        
        else:
            sys.exit()
    
    def collect_data(self, agent: int = 2, battery: int = 0):
        if agent == 2:
            self.observation = np.array(collect_data(agent=agent, battery=battery, store=False), np.uint64)
            return self.observation
        else:
            return np.array(collect_data(agent=agent, battery=battery, store=False), np.uint64)
    
    def render(self, mode="human"):
        pass

    def close(self):
        pass
    
    def startEpisode(self):
        os.remove(os.path.join(home, '.done'))
    
    def endEpisode(self):
        with open(os.path.join(home, '.done'), 'w') as _:
            pass
    
    def saveObservation(self, observation):
        self.observation = observation
    
    def reward_function(self, I: int, T: list, S_prime: int, t_optimal: int = 0, t_user: int = 0, _delta: float = 1.0):
        T_prime = T[1]
        delta_T = T_prime - T[0]

        if T_prime < self.T_L:
            return -1000.0 # -np.inf
        elif T_prime > self.T_H:
            return -1000.0 # -np.inf

        if T_prime < self.T_L and S_prime <= self.S_L:
            reward = - (T_prime - self.T_L) * delta_T * self._alpha[0] * self._omega[0] + I * (self.S_L - S_prime) * self._beta[0] + 0
        elif (T_prime >= self.T_L and T_prime <= self.T_H) and S_prime <= self.S_L:
            reward = - delta_T * self._alpha[1] * self._omega[0] + I * (self.S_L - S_prime) * self._beta[0] + 0
        elif T_prime > self.T_H and S_prime <= self.S_L:
            reward = - (T_prime - self.T_H) * delta_T * self._alpha[2] * self._omega[0] + I * (self.S_L - S_prime) * self._beta[0] + 0

        elif T_prime < self.T_L and (S_prime > self.S_L and S_prime <= self.S_H):
            reward = - (T_prime - self.T_L) * delta_T * self._alpha[0] * self._omega[1] + 0 - _gamma * abs(t_user - (_delta * t_optimal))
        elif (T_prime >= self.T_L and T_prime <= self.T_H) and (S_prime > self.S_L and S_prime <= self.S_H):
            reward = - delta_T * self._alpha[1] * self._omega[1] + 0 - _gamma * abs(t_user - (_delta * t_optimal))
        elif T_prime > self.T_H and S_prime <= (S_prime > self.S_L and S_prime <= self.S_H):
            reward = - (T_prime - self.T_H) * delta_T * _alpha[2] * self._omega[1] + 0 - _gamma * abs(t_user - (_delta * t_optimal))
        
        elif T_prime < self.T_L and S_prime > self.S_H:
            reward = - (T_prime - self.T_L) * delta_T * self._alpha[0] * self._omega[2] + (1.0 * self._beta[1]) / (I * (S_prime - self.S_H)) + 0
        elif (T_prime >= self.T_L and T_prime <= self.T_H) and S_prime > self.S_H:
            reward = - delta_T * self._alpha[1] * self._omega[2] + (1.0 * self._beta[1]) / (I * (S_prime - self.S_H)) + 0
        elif T_prime > self.T_H and S_prime > self.S_H:
            reward = - (T_prime - self.T_H) * delta_T * self._alpha[2] * self._omega[2] + (1.0 * self._beta[1]) / (I * (S_prime - self.S_H)) + 0
        else:
            pass
        
        return reward   

    
# test function
def test():
    env = gym.make('ACRLF-v0', t_optimal=15, S_prime=45, _delta=1)

    observation = env.reset()
    
    for _ in range(10):        
        action = env.action_space.sample()
        # action = Agent2(observation)

        observation, reward, done, info = env.step(action)

        print(observation, reward, done)

        notification_app = multiprocessing.Process(target=NotificationApp, args=(60, 120, 180, 15, 1))
        notification_app.start()

        user_input = np.array(client(50, 1), np.uint64)[1]

        notification_app.join()

        print("User Input: {}".format(user_input))

        if done:
            observation = env.reset()
    
    env.close()

if __name__ == '__main__':
    test()
