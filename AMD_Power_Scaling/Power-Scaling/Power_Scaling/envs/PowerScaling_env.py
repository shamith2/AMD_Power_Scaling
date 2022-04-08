# PowerScaling_env.py
# creates new environment PowerScaling
# 
# Copyright (c) 2022 Shamith Achanta
# Report Bugs to Shamith Achanta <shamith2@illinois.edu>
#

import gym
from gym import spaces
import numpy as np
import subprocess
# import time
import os

class PowerScaling(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, continuous: bool = False):
        # state size
        self.size = 5
        # bounds for state space
        lower_bnds = np.zeros(shape=(self.size,))
        upper_bnds = np.array([100.0, 2, 100.0, 100.0, 100.0])
        # state space: 15; continuous
        self.observation_space = spaces.Box(lower_bnds, upper_bnds, dtype=np.float64)
        self.continuous = continuous
        self.prev_state = None
        self.state = None
        self.ctime = 0

        # action space
        if self.continuous:
            self.action_list = None
            self.action_space = spaces.Box(-1, 100, shape=(1,), dtype=np.int32)
        else:
            self.action_list = np.array([22, 35, 54, 66, 73])
            self.action_space = spaces.Discrete(len(self.action_list))
            

    def step(self, action):
        # hyperparamters
        _tau = 50
        _omega = 15 * 60
        _Omega = 10
        _theta = 45 * 60
        _gamma = 70
        _no_reward = 0
        _less_penal = -10
        _less_reward = 2
        _more_penal = -20
        _more_reward = 5
        _invalid = -1

        reward = 0
        done = False
        info = {}

        # action should strictly be between -1 and 100; -1 for do nothing
        if self.continuous:
            action = np.clip(action, -1, 100).astype(np.int32)
        else:
            assert self.action_space.contains(action), f"{action!r} ({type(action)}) invalid "

        if self.continuous:
            _action = action[0]
        else:
            _action = self.action_list[action]

        # save previous state
        if self.state is None:
            self.prev_state = np.array(self.collect_state(), np.float64)
        else:
            self.prev_state = np.array(self.state, np.float64)

        # change battery charging rate
        # time.sleep(1)

        # get next state
        self.state = np.array(self.collect_state(), np.float64)

        # how long the system is charging
        if self.prev_state[1] == np.float64(0) and self.state[1] == np.float64(1):
            self.ctime = 0
        elif self.prev_state[1] == np.float64(1) and self.state[1] == np.float64(1):
            self.ctime = int(time.time()) - self.ctime

        # calculate reward
        if _action < 20 or _action > 80:
            reward = -np.inf
        
        else:
            # slow charging
            if _action < _tau:
                reward = _more_reward
                    
                # if battery is discharging and SoC has not reached _gamma
                if self.prev_state[1] != np.float64(0) and self.state[1] == np.float64(0) and self.state[0] < _gamma:
                    if self.ctime > 0 and self.ctime < _omega:
                        reward = _more_penal
                    else:
                        reward = _more_reward
                        
                # if battery temperature is over _theta
                if self.state[2] > _theta:
                    reward = _less_penal
                
                if self.prev_state[1] == np.float64(0) and self.state[1] == np.float64(0):
                    reward = _no_reward            
                    
            else:
                reward = _less_reward
                    
                # if battery is charging for time >= _omega and SoC has reached _gamma
                if self.prev_state[1] == np.float64(1) and self.state[1] == np.float64(1) and self.state[0] >= _gamma:
                    if self.ctime >= _Omega: 
                        reward = _more_penal
                    else:
                        reward = _more_reward
                        
                # if battery temperature is over _theta
                if self.state[2] > _theta:
                    reward = _more_penal
                
                if self.prev_state[1] == np.float64(0) and self.state[1] == np.float64(0):
                    reward = _no_reward
        
        return self.state, reward, done, info

    def reset(self):
        return np.array(self.collect_state(), np.float64)
    
    def render(self, mode="human"):
        pass

    def create(self, header, dir="results"):
        if not os.path.isdir(dir):
            os.mkdir(dir)
        
        with open(os.path.join(dir, 'report.txt'), 'w') as f:
            f.write(header)
            f.write('\n')

    def write(self, obj, dir="results"):
        with open(os.path.join(dir, "report.txt"), 'a') as f:
            for i, o in enumerate(obj):
                if i != 0:
                    f.write("," + str(o))
                else:
                    f.write(str(o))
            f.write('\n')

    def close(self):
        pass

    def collect_state(self):
        memInfo="""free -t | awk 'NR==4{printf "%f", $3*100/$2}'"""
        cpuInfo="""top -bn1 | awk 'NR==3' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{printf "%f", 100-$1}'"""
        # TODO: GPU USAGE
        gpuInfo="""echo -n '0'"""
        
        battDir="""/sys/class/power_supply/"""
        battSoCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/capacity | awk '{printf "%f", $1}'"""
        # capacity level status: Normal: 1, Full: 2
        battCapLvlInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/capacity_level | awk '{if($1 == "Normal") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else {printf "%d", 0}}'"""
        # plug-in status: Discharging: 0, Charging: 1, Full: 2
        battStatusInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/status | awk '{if($1 == "Charging") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else {printf "%d", 0}}'"""
        battVolInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/voltage_now | awk '{printf "%ld", $1}'"""
        battDVInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/voltage_min_design | awk '{printf "%ld", $1}'"""
        battPowInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/power_now | awk '{printf "%ld", $1}'"""
        battCapInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_now | awk '{printf "%ld", $1}'"""
        battFCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_full | awk '{printf "%ld", $1}'"""
        battDCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_full_design | awk '{printf "%ld", $1}'"""
        battCycleInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/cycle_count | awk '{printf "%d", $1}'"""
        battTempInfo="""acpi -t | awk '{print $(NB==1)}' | sed 's/.*, *\([0-9.]*\)* degrees C*/\\1/' | awk '{printf "%f", $1}'"""
        battChargeRate="""upower -e | grep 'BAT' | xargs -I{} upower -i {} | grep energy-rate | tr -d -c 0-9. | awk '{printf "%f", $1}'"""
        
        commands = [battSoCInfo, battStatusInfo, battTempInfo, battChargeRate, cpuInfo]

        # data := (state, action, next state, reward, done)
        # state := (TIME,MEMORY_USAGE,CPU_USAGE,GPU_USAGE,BATTERY_CAPACITY,BATTERY_STATUS,BATTERY_VOLTAGE,BATTERY_POWER,BATTERY_ENERGY)

        stateEntry = tuple()

        # stateEntry += (int(time.time()),)

        for command in commands:
            process = subprocess.run(command, capture_output=True, shell=True)
                
            output = process.stdout.decode('utf-8')
            if output != '':
                stateEntry += (output,)
            else:
                stateEntry += (0, )

        return stateEntry
    
# test function
def test(env):
    env = gym.make('Power_Scaling:PowerScaling-v0')
    observation = env.reset()
    action = None
    reward = None
    total_reward = 0
    env.create("[SoC, Charging Status, Battery Temperature, Battery Charging Rate, CPU Usage],action,reward")
    
    for _ in range(10):
        env.write([observation, action, reward])
        action = np.random.randint(1, 5)
        observation, reward, done, info = env.step(action)
        total_reward += reward
    
    env.close()

    return total_reward

if __name__ == '__main__':
    test(PowerScaling())
