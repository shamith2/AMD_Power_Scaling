# script for rendering results

import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

def plot_figure(env_dir, result_dict, timestep, seed, goal):
    div = len(result_dict['bcq'])
    plt.figure()
    plt.plot(range(1, div+1), result_dict['bcq'], 'y', label="offline bcq")
    plt.plot(range(1, div+1), result_dict['dqn'], 'b', label="online dqn")
    plt.title("Offline vs Online deep Q-Network")
    
    plt.hlines(float(goal), 1, div, 'k', label='goal')
    plt.hlines(float(result_dict['buf'][0]), 1, div, 'g', label='buffer dqn')
    plt.legend()
    plt.xlabel("timesteps")
    plt.ylabel("reward")
    plt.savefig(env_dir + "_" + str(timestep) + "_" + str(seed) + ".png")

def render_script(args):
    results = dict.fromkeys(['bcq', 'dqn', 'buf'])

    tstep = args.num_steps
    env_name = args.env
    seed = args.seed
    goal = args.goal

    for keys, dir in zip(results.keys(), ["../../results/BCQ_", "../../results/behavioral_", "../../results/buffer_performance_"]):
        results[keys] = np.load(dir + str(env_name) + "_" + str(tstep) + "_" + str(seed) + ".npy")
    
    plot_figure("../../plots/" + str(env_name), results, str(tstep), seed, goal)
