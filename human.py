import pandas as pd
import numpy as np
import copy
from env import MurderGame

# inital
mg = MurderGame(gridNum=20,
                peopleNum=200)

# human play
tb = mg.createTb()
tbInit = copy.deepcopy(tb)
tbHuman, totalRewardHuman = mg.play(tb)
print('totalRewardHuman:',-totalRewardHuman)