import unittest
import random

def generate_datapoint():
    choose = random.randint(1, 15)

    datapoints = {}
    datapoints['1'] = [10,0.826997,0.0,0,30,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,15]
    datapoints['2'] = [100,0.826997,0.0,0,35,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,16]
    datapoints['3'] = [200,0.826997,0.0,0,42,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,17]
    datapoints['4'] = [350,0.826997,0.0,0,44,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,18]
    datapoints['5'] = [425,0.826997,0.0,0,47,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,19]
    datapoints['6'] = [555,0.826997,0.0,0,47,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,18]
    datapoints['7'] = [673,0.826997,0.0,0,45,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,17]
    datapoints['8'] = [776,0.826997,0.0,0,41,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,16]
    datapoints['9'] = [779,0.826997,0.0,0,39,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,16]
    datapoints['10'] = [834,0.826997,0.0,0,37,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,16]
    datapoints['11'] = [924,0.826997,0.0,0,37,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,16]
    datapoints['12'] = [1100,0.826997,0.0,0,38,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,18]
    datapoints['13'] = [1200,0.826997,0.0,0,42,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,20]
    datapoints['14'] = [2500,0.826997,0.0,0,43,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,20]
    datapoints['15'] = [2530,0.826997,0.0,0,45,5000000,5000000,5000000,2,2,5000000,5000000,0,-1,21]

    return datapoints[str(choose)]


def create_dummy_dataset():
    with open("../../datasets/dummy_dataset", "w") as f:
        f.write("TIME(int),MEMORY_USAGE(%),CPU_USAGE(%),GPU_USAGE(%),SoC(%),BATTERY_CAPACITY(int),BATTERY_FULL_CAPACITY(int),BATTERY_DESIGN_CAPACITY(int),BATTERY_CAPACITY_LEVEL(int),BATTERY_STATUS(int),BATTERY_VOLTAGE(int),BATTERY_DESIGN_VOLTAGE(int),BATTERY_POWER(int),BATTERY_CYCLES(int),BATTERY_TEMP(C)\n")
        
        f.write(generate_datapoint())

class Test_Agent(unittest.TestCase):
    def test_action(self):
        self.assertEqual(0, 0)

if __name__ == "__main__":
    unittest.main()