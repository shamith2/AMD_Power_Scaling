import unittest
import numpy as np
import imp
utils = imp.load_source("utils", "../../BCQ/discrete_BCQ/utils.py")
discrete_BCQ = imp.load_source("dicrete_BCQ", "../../BCQ/discrete_BCQ/discrete_BCQ.py")

def generate_datapoints():
    # datapoint := TIME(int),MEMORY_USAGE(%),CPU_USAGE(%),SoC(%),IS_PLUGGED(int),CPU_TEMP(C),CPU_POWER(W),BATTERY_TEMP(C),GPU_TEMP(C),GPU_POWER(W),actions (Charge rate)
    datapoints = {}
    # datapoints['1'] = [1648673441,60,11.2,45,1,41,46.79905188,41,40,38.60300255,55]
    # datapoints['2'] = [1648673461,60,7,45,1,40,47.20767933,42,40,39.39644662,60]
    # datapoints['3'] = [1648673481,72.4,12.1,45,1,39,47.12066628,43,37,38.46692523,62]
    # datapoints['4'] = [1648673501,71.3,13.1,46,1,39,48.51086814,43,37,39.26337863,56]
    # datapoints['5'] = [1648673521,77,11.7,46,1,40,49.52698944,43,38,39.95144624,54]
    # datapoints['6'] = [1648673541,80,9.4,46,1,40,50.8761083,43,37,39.2566372,45]
    # datapoints['7'] = [1648673561,80.2,7.9,46,1,39,50.67326338,42,39,39.22671349,44]
    # datapoints['8'] = [1648673581,79.9,10.9,46,1,40,49.16961077,42,40,39.785852,40]
    # datapoints['9'] = [1648673601,75,9.8,46,1,40,50.0497158,41,37,39.13916291,50]
    # datapoints['10'] = [1648673621,73.9,7,46,1,40,49.57465595,42,36,39.1560373,55]
    # datapoints['11'] = [1648673641,74.2,8.3,46,1,40,49.90958722,42,37,38.42886413,53]
    # datapoints['12'] = [1648673661,64.8,8.3,46,1,41,50.0765822,42,37,37.65436309,60]
    # datapoints['13'] = [1648673681,63.1,9.6,47,1,39,48.41704385,45,38,37.17722859,49]
    # datapoints['14'] = [1648673701,64.8,9,47,1,39,47.83311617,44,37,36.50978098,39]

    # datapoint := [battSoCInfo, battStatusInfo, battTempInfo, battChargeRate, cpuInfo]
    datapoints['1'] = [45,1,0,0,11.2]
    datapoints['2'] = [45,1,0,0,7]
    datapoints['3'] = [45,1,0,0,12.1]
    datapoints['4'] = [46,1,0,0,13.1]
    datapoints['5'] = [46,1,0,0,11.7]
    datapoints['6'] = [46,1,0,0,9.4]
    datapoints['7'] = [46,1,0,0,7.9]
    datapoints['8'] = [46,1,0,0,10.9]
    datapoints['9'] = [46,1,0,0,9.8]
    datapoints['10'] = [46,1,0,0,7]
    datapoints['11'] = [46,1,0,0,8.3]
    datapoints['12'] = [46,1,0,0,8.3]
    datapoints['13'] = [47,1,0,0,9.6]
    datapoints['14'] = [47,1,0,0,9]

    actions = {}
    actions['1'] = 55
    actions['2'] = 60
    actions['3'] = 62
    actions['4'] = 56
    actions['5'] = 54
    actions['6'] = 45
    actions['7'] = 44
    actions['8'] = 40
    actions['9'] = 50
    actions['10'] = 55
    actions['11'] = 53
    actions['12'] = 60
    actions['13'] = 49
    actions['14'] = 39

    return datapoints, actions

class Test_Agent(unittest.TestCase):
    def test_action(self):
        parameters = {
            # Exploration
            "start_timesteps": 50,#1e3,
            "initial_eps": 0.1,
            "end_eps": 0.1,
            "eps_decay_period": 1,
            # Evaluation
            "eval_freq": 100,#5e3,
            "eval_eps": 0,
            # Learning
            "discount": 0.99,
            "buffer_size": 1e6,
            "batch_size": 64,
            "optimizer": "Adam",
            "optimizer_parameters": {
                "lr": 3e-4
            },
            "train_freq": 1,
            "polyak_target_update": True,
            "target_update_freq": 1,
            "tau": 0.005
        }

        env, _, state_dim, num_actions = utils.make_env("Power_Scaling:PowerScaling-v0", None)

        # Initialize and load policy
        policy = discrete_BCQ.discrete_BCQ(
            0,
            num_actions,
            state_dim,
            "cpu",
            0.3,
            parameters["discount"],
            parameters["optimizer"],
            parameters["optimizer_parameters"],
            parameters["polyak_target_update"],
            parameters["target_update_freq"],
            parameters["tau"],
            parameters["initial_eps"],
            parameters["end_eps"],
            parameters["eps_decay_period"],
            parameters["eval_eps"]
        )

        avg_reward = 0
        state = env.reset()
        env.create("state,actual_action,pred_action,reward", ".")
        datapoints, actions = generate_datapoints()
        
        actual_action = None
        pred_action = None
        reward = None
        actual_results = []
        pred_results = []

        for i in range(1, len(datapoints) + 1):
            state = datapoints[str(i)]
            action = policy.select_action(np.array(state), eval=True)
            
            if action < 50:
                pred_action = "__slow__"
            else:
                pred_action = "__fast__"
            
            if actions[str(i)] < 50:
                actual_action = "__slow__"
            else:
                actual_action = "__fast__"


            env.write([state, actual_action, pred_action, reward], ".")
            actual_results.append(actual_action)
            pred_results.append(pred_action)

            state, reward, _, _ = env.step(action)
            avg_reward += reward
        
        self.assertEqual(actual_results, pred_results)

if __name__ == "__main__":
    unittest.main()