# __init__.py
# registers the environments with gym
# 
# Copyright (c) 2022 Shamith Achanta
# Report Bugs to Shamith Achanta <shamith2@illinois.edu>
#

from gym.envs.registration import register

register(
    id='PowerScaling-v0',
    entry_point='Power_Scaling.envs:PowerScaling',
    max_episode_steps=float('inf')
)
