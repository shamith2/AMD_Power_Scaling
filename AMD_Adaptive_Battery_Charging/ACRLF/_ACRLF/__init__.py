# __init__.py
# registers the environments with gym
# 
# Copyright (c) 2023 Advanced Micro Devices Inc.
# Report Bugs to Shamith Achanta <Shamith.Achanta@amd.com>
#

import gymnasium as gym

gym.register(
    id='ACRLF-v0',
    entry_point='_ACRLF.envs:ACRLF',
    nondeterministic=True,
    max_episode_steps=float('inf')
)
