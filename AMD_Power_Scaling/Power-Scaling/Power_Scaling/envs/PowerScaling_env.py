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
import time
import os
import sys
import torch
from datetime import datetime

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
        self.nnSpace = None
        self.ctime = 0

        # Hyperparameters
        self._tau = 50
        self._omega = 15 * 60
        self._Omega = 45 * 60
        self._theta = 45
        self._gamma = 70
        self._no_reward = 0
        self._less_penal = -10
        self._less_reward = 2
        self._more_penal = -20
        self._more_reward = 7
        self._invalid = -1

        # action space
        if self.continuous:
            self.action_list = None
            self.action_space = spaces.Box(-1, 100, shape=(1,), dtype=np.int32)
        else:
            self.action_list = np.array([22, 35, 54, 66, 73])
            self.action_space = spaces.Discrete(len(self.action_list))
            

    def step(self, action):
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
        time.sleep(1)

        # get next state
        self.state, self.nnSpace = self.collect_state()

        # how long the system is charging
        if self.prev_state[1] == np.float64(3) and self.state[1] == np.float64(1):
            self.ctime = 0
        elif self.prev_state[1] == np.float64(1) and self.state[1] == np.float64(1):
            self.ctime = int(time.time()) - self.ctime

        # calculate reward
        reward = self.reward_function_logic(_action)
        # reward = self.reward_function_nn(self.nnSpace)
        
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
        timeInfo="""date +%s"""
        memInfo="""free -t | awk 'NR==4{printf "%f", $3*100/$2}'"""
        cpuInfo="""top -bn1 | awk 'NR==3' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{printf "%f", 100-$1}'"""
        # TODO: GPU USAGE
        gpuInfo="""echo -n '0'"""
        
        battDir="""/sys/class/power_supply/"""
        battSoCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/capacity | awk '{printf "%f", $1}'"""
        # capacity level status: Normal: 1, Full: 2
        battCapLvlInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/capacity_level | awk '{if($1 == "Normal") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else if($1 == "High") {printf "%d", 3} else if($1 == "Critical") {printf "%d", 4} else if($1 == "Low") {printf "%d", 5} else {printf "%d", 0}}'"""
        # plug-in status: Discharging: 0, Charging: 1, Full: 2
        battStatusInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/status | awk '{if($1 == "Charging") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else if($1 == "Discharging") {printf "%d", 3} else {printf "%d", 0}}'"""
        battVolInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/voltage_now | awk '{printf "%ld", $1}'"""
        battDVInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/voltage_min_design | awk '{printf "%ld", $1}'"""
        battPowInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/power_now | awk '{printf "%ld", $1}'"""
        battCapInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_now | awk '{printf "%ld", $1}'"""
        battFCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_full | awk '{printf "%ld", $1}'"""
        battDCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_full_design | awk '{printf "%ld", $1}'"""
        battCycleInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/cycle_count | awk '{printf "%d", $1}'"""
        battTempInfo="""acpi -t | awk '{print $(NB==1)}' | sed 's/.*, *\([0-9.]*\)* degrees C*/\\1/' | awk '{printf "%f", $1}'"""
        battChargeRate="""upower -e | grep 'BAT' | xargs -I{} upower -i {} | grep energy-rate | tr -d -c 0-9. | awk '{printf "%f", $1}'"""

        # data := (state, action, next state, reward, done)
        # state
        state_commands = [battSoCInfo, battStatusInfo, battTempInfo, battChargeRate, cpuInfo]
        battery_commands = [battSoCInfo, timeInfo, battStatusInfo, battCapInfo, battCycleInfo, battVolInfo, battTempInfo, battChargeRate]
        doubleVar_commands = [battFCInfo, battDCInfo]
        stateEntry = tuple()
        batteryEntry = tuple()

        for command in state_commands:
            process = subprocess.run(command, capture_output=True, shell=True)
            output = process.stdout.decode('utf-8')
            
            if output != '':
                stateEntry += (output,)
            else:
                stateEntry += (0, )
        
        for command in battery_commands:
            process = subprocess.run(command, capture_output=True, shell=True)
            output = process.stdout.decode('utf-8')
            
            if output != '':
                batteryEntry += (output,)
            else:
                batteryEntry += (0, )
        
        for i, command in enumerate(doubleVar_commands, start=1):
            process = subprocess.run(command, capture_output=True, shell=True)
            output = process.stdout.decode('utf-8')

            if output != '':
                if i % 2 != 0:
                    temp = output
                else:
                    temp = temp / output
            else:
                temp = 0
            
            if i % 2 == 0:
                batteryEntry += (temp,)

        return np.array(stateEntry, np.float64), np.array(batteryEntry, np.float64)
    
    def reward_function_logic(self, action):
        if action < 20 or action > 80:
            reward = -np.inf
        else:
            # slow charging
            if action < self._tau:
                # if battery is discharging and SoC has not reached _gamma
                if self.prev_state[1] == np.float64(1) and self.state[1] == np.float64(3) and self.state[0] < self._gamma:
                    if self.ctime > 0 and self.ctime < self._omega:
                        reward = self._more_penal
                # if battery temperature is over _theta
                elif self.state[2] > self._theta:
                    reward = self._less_penal
                else:
                    reward = self._more_reward
            else:
                # if battery is charging for time >= _omega and SoC has reached _gamma
                if self.prev_state[1] == np.float64(1) and self.state[1] == np.float64(1) and self.state[0] >= self._gamma:
                    if self.ctime >= self._Omega: 
                        reward = self._more_penal
                # if battery temperature is over _theta
                elif self.state[2] > self._theta:
                    reward = self._more_penal
                else:
                    reward = self._less_reward
        
        return reward
    
    def reward_nn(self, input_size, hidden_layers, output_size):
        class Feedforward(torch.nn.Module):
            def __init__(self, input_size, hidden_layers, output_size):
                super(Feedforward, self).__init__()
                self.input_size = input_size
                self.num_hidden_layers = hidden_layers
                self.output_size = output_size
                # layers
                self.fc1 = torch.nn.Linear(self.input_size, self.num_hidden_layers)
                self.fc2 = torch.nn.Linear(self.num_hidden_layers, self.num_hidden_layers)
                self.fc3 = torch.nn.Linear(self.num_hidden_layers, self.output_size)
                # activation functions
                self.relu = torch.nn.ReLU()
                self.softmax = torch.nn.Softmax()
            
            def forward(self, x):
                hidden_layer_1 = self.fc1(x)
                relu_1 = self.relu(hidden_layer_1)
                hidden_layer_2 = self.fc2(relu_1)
                relu_2 = self.relu(hidden_layer_2)
                output_layer = self.fc3(relu_2)
                output_layer = self.softmax(output_layer)
                
                return output_layer
        
        reward_model = Feedforward(input_size, hidden_layers, output_size)

        return reward_model
    
    def train_reward_nn(self, train_data, train_epochs, batch_size):
        reward_model = self.reward_nn(len(train_data), 10, 1)
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(reward_model.parameters(), lr=0.001, momentum=0.9)
        trainloader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=2)
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if device == torch.device('cuda'):
            reward_model.to(device)

        # loop over the dataset multiple times
        for epoch in range(train_epochs):
            running_loss = 0.0
            for i, data in enumerate(trainloader, 0):
                # get the inputs; data is a list of [inputs, labels]
                if device == torch.device('cuda'):
                    inputs, labels = data[0].to(device), data[1].to(device)
                else:
                    inputs, labels = data

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                outputs = reward_model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                # print statistics
                running_loss += loss.item()
                # print every batch_size mini-batches
                if i % batch_size == batch_size - 1:
                    print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / batch_size:.3f}')
                    running_loss = 0.0
    
        print("Saving Model...")
        if not os.path.exists("./models"):
            os.makedirs("./models")
        
        torch.save(reward_model, "./models/" + "reward_model_" + str(batch_size) + "_" + str(datetime.now().strftime("%m-%d-%H:%M:%S")) + ".pth")
    
    def reward_function_nn(self, battery_parameters):
        filename = "./models/" + "reward_model.pth"
        if not os.path.exists(filename):
            print("No file named 'reward_model.pth'")
            sys.exit(-1)
        else:
            reward_model = torch.load(filename)
        
        SoH = reward_model(battery_parameters[:, -1])

        if SoH >= 0.8:
            reward = self._more_reward
        if SoH > 0.5 and SoH < 0.8:
            reward = self._less_reward
        else:
            reward = self._more_penal

        return reward      

    
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
