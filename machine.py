import pandas as pd
import numpy as np
import copy
from env import MurderGame

# inital
mg = MurderGame(gridNum=5,
                peopleNum=5)
tb = mg.createTb()
tbInit = copy.deepcopy(tb)    

# machine play

def randomPolice(tb):
    guess = np.random.choice(
        np.r_[-999, np.random.choice(tb.people[tb.statue == 'live'])],p=[0.5,0.5])
    return(guess)

def Test_Round():
    tb = copy.deepcopy(tbInit)
    time = 0
    totalRewardMachine = 0
    done = False
    civilLiveLast = mg.civilNum
    while not done:
        time = time+1
        policeGuess = randomPolice(tb)
        tb, reward, done, info = mg.machine_step(
            policeGuess, tb, time, civilLiveLast)
        totalRewardMachine = totalRewardMachine+reward
        civilLiveLast = info.get('civilLive')
    print('totalReward:',-totalRewardMachine)
    return -totalRewardMachine
reward_test=0

for i in range(100):
    reward_test += Test_Round()

test=reward_test/100

print(test)


