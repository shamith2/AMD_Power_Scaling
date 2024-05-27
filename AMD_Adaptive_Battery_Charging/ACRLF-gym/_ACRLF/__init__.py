# __init__.py
# registers the environments with gym
#

from gym.envs.registration import register

register(
    id='ACRLF-v0',
    entry_point='_ACRLF.envs:ACRLF',
    max_episode_steps=float('inf')
)
