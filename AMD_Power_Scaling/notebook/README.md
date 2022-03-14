# Notebook:

## 02/10/2022 and 02/11/2022:

### evaluated algorithms for batch-RL:
- used Discrete Batch-Constrained deep Q-Learning (BCQ)
- to evaluate LunarLander-v2
- with 
    - online deep Q-network (DQN) [agent learns by interacting the environment; also as behavioral policy]
    - offline BCQ [agent learns from data/buffer without interacting with the environment]
    - buffer DQN [trained DQN evaluated on data/buffer used to train offline BCQ]
- result: offline BCQ better than buffer DQN; offline BCQ matches DQN; trained on same amount of data

- Batch Deep RL: data is fixed and no further interactions with the environment occur
- Behavior Policy: is the policy that is being used by an agent for action select i.e agent follows this policy to interact with the environment
- Target Policy: is the policy that an agent is trying to learn i.e agent is learning value function for this policy
- off-policy: behavioral-policy != target-policy
- ^(better than on-policy)
- on-policy: behavioral-policy == target-policy

- unlikely-action: eliminate actions with prob < BCQ_threshold; threshold = 0 returns Q-learning; threshold = 1 returns an imitator of the actions contained in the batch

- extrapolation-error: when selecting actions a', such that (s', a') is distant from data contained in the batch, the estimate Q'(s', a') may be arbitrarily poor
- ^(can be mitigated when agent has interactions with the enviroment and on-policy)

### apply to AMD Power Scaling project:
- discrete action space
- fully-observable Markov Decision Process
- Batch Deep RL and Off Policy

- data/buffer: (state, action, next_state, reward, done, [done_float, episode_start])

- !(extrapolation-error)
- ?(discount), ?(explore-vs-exploit: eps), ?(unlikely-action)

## 02/12/2022:

### apply to AMD Power Scaling project:
- states: available charging rates (state space continuous)
- actions: increase charging rate, decrease charging rate, do nothing

## 02/16/2022:

### trends in data for Power Scaling:
- time vs charging status => charging pattern over time
- current [power, voltage], SoC, Capacity [Now, Full, Design] => SoH 

## 03/04/2022:

### AMD Updates:
- cpu benchmark: cinebench to get battery temp with cpu load
- gpu benchmark
