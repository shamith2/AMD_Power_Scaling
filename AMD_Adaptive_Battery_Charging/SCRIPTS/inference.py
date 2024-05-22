import gym

home = os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging')
sys.path.insert(0, os.path.join(home, 'ACRLF-gym'))
import _ACRLF

sys.path.insert(0, os.path.join(home, 'GUI'))
from gui import *

from pipe import *

def user_input():
    pass


if __name__ == '__main__':
    env = gym.make('ACRLF-v0')

    while True:
        # observation_1 := (t_optimal, state_of_charge)
        observation_1 = env.collect_data(agent=1, battery=0)
        
        # action_1 = differential parameter
        action_1 = Agent_1(observation_1)

        # observation_2 := (battery_temperature, state_of_charge, battery_capacity, t_optimal, charge_rate)
        observation_2 = env.collect_data(agent=2, battery=0)

        # observation_2 := (battery_temperature, state_of_charge, battery_capacity, weighed_t_optimal, charge_rate)
        observation_2[3] = observation_2[3] * action_1
        
        # action_2 := charge_rate
        action_2 = Agent_2(observation_2)

        observation_2, reward, done, info = env.step(action_2)

        client(100)

        if done:
            sys.exit()