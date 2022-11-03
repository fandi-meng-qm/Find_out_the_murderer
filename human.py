import pandas as pd
import numpy as np
import copy
from env import MurderGame

# inital
mg = MurderGame(gridNum=10,
                peopleNum=10)

# human play
tb = mg.createTb()
tbInit = copy.deepcopy(tb)
tbHuman, totalRewardHuman = mg.play(tb)
print('totalRewardHuman:',-totalRewardHuman)