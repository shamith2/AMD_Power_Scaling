# __init__.py
# registers the environments with gym
#

import gymnasium as gym

gym.register(
    id='ACRLF-v0',
    entry_point='_ACRLF.envs:ACRLF',
    nondeterministic=True,
    max_episode_steps=float('inf')
)
