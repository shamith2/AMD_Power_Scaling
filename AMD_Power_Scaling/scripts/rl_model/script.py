import os
import argparse
from render import *

def run_script(args):
    steps = args.num_steps
    env_name = args.env
    alg_name = args.alg
    seed = args.seed

    if args.episodic:
        train_beh = lambda x: "python3 ./BCQ/discrete_BCQ/main.py --env=" + str(env_name) + " --max_timesteps=" + str(x) + " --seed=" + str(seed) + " --episodic --train_behavioral"
        gen_buff = lambda x: "python3 ./BCQ/discrete_BCQ/main.py --env=" + str(env_name) + " --max_timesteps=" + str(x) + " --seed=" + str(seed) + " --episodic --generate_buffer"
        train_bcq = lambda x: "python3 ./BCQ/discrete_BCQ/main.py --env=" + str(env_name) + " --max_timesteps=" + str(x) + " --seed=" + str(seed) + " --episodic"
    else:
        train_beh = lambda x: "python3 ./BCQ/discrete_BCQ/main.py --env=" + str(env_name) + " --max_timesteps=" + str(x) + " --seed=" + str(seed) + " --train_behavioral"
        gen_buff = lambda x: "python3 ./BCQ/discrete_BCQ/main.py --env=" + str(env_name) + " --max_timesteps=" + str(x) + " --seed=" + str(seed) + " --generate_buffer"
        train_bcq = lambda x: "python3 ./BCQ/discrete_BCQ/main.py --env=" + str(env_name) + " --max_timesteps=" + str(x) + " --seed=" + str(seed)
    
    online_dnq = lambda x, y: ". baselines/bin/activate && cd baselines && python3 -m baselines.run --alg=" + str(alg_name) + " --env=" + str(env_name) + \
                    " --num_timesteps=" + str(x) + " --save_path=../models/" + str(alg_name.upper()) + "_" + str(env_name) + "_" + str(x) + "_" + str(y) + \
                    " --log_path=../logs/" + str(alg_name.upper()) + "_"+ str(env_name) + "_" + str(x) + "_" + str(y) + " --seed=" + str(seed) + \
                    " && cd .. && deactivate"

    for command in [train_beh, gen_buff, train_bcq]:
        os.system(command(steps))

    for dir in ["./results/BCQ_", "./results/behavioral_", "./results/buffer_performance_"]:
        os.system("mv " + dir + str(env_name) + "_" + str(seed) + ".npy " + dir + str(env_name) + "_" + str(steps) + "_" + str(seed) + ".npy")

    #os.system(online_dnq(steps, seed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="LunarLander-v2")                      # OpenAI gym environment name
    parser.add_argument("--goal", default=200)                                  # sucess score / goal
    parser.add_argument("--seed", default=0, type=int)                          # Sets Gym, PyTorch and Numpy seeds
    parser.add_argument("--alg", default="deepq")                               # algorithm for baselines
    parser.add_argument("--num_steps", default=500000)                          # Max time steps to run environment or train for
    parser.add_argument("--render_only", default=0)                             # only render or run_script and render
    parser.add_argument("--include_baselines", default=0)                       # include baselines result while rendering
    parser.add_argument("--episodic", action="store_true")                      # If true, task is episodic
    args = parser.parse_args()

    if str(args.render_only) == '0':
        run_script(args)
        render_script(args)
    else:
        render_script(args)
