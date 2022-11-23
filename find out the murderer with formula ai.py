
# %% Import Modules
from plotly.offline import plot
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import copy

# %% Class Murder Game


class KillerNear():

    def __init__(self):
        pass

    def kill(self, tb, killPeopleOneStep=1):
        tobeKill = np.logical_and(tb.role == 'civil', tb.statue == 'live')
        distTobeKillRecip = 1/tb.dist[tobeKill]
        peopleTobeKill = tb.people[tobeKill]
        probTobeKill = distTobeKillRecip/np.sum(distTobeKillRecip)
        deaths = np.random.choice(peopleTobeKill,
                                  size=killPeopleOneStep,
                                  p=probTobeKill,
                                  replace=False)
        return(deaths)


class KillerFar():

    def __init__(self):
        pass

    def kill(self, tb, killPeopleOneStep=1):
        tobeKill = np.logical_and(tb.role == 'civil', tb.statue == 'live')
        distTobeKill = tb.dist[tobeKill]
        peopleTobeKill = tb.people[tobeKill]
        probTobeKill = distTobeKill/np.sum(distTobeKill)
        deaths = np.random.choice(peopleTobeKill,
                                  size=killPeopleOneStep,
                                  p=probTobeKill,
                                  replace=False)
        return(deaths)


class MurderGame():

    def __init__(self,
                 gridNum=4,
                 peopleNum=3,
                 killerNum=1,
                 killerKind='Near'):
        self.gridNum = gridNum
        self.grid = np.r_[0:gridNum]
        self.peopleNum = peopleNum
        self.killerNum = killerNum
        self.killerKind = killerKind
        self.civilNum = peopleNum-killerNum
        self.people = np.r_[0:peopleNum]
        self.killer = self.defineKiller()
        self.peopleXy, self.peopleXyDf = self.sampleXy()

    def defineKiller(self):
        killer = np.random.choice(self.people,
                                  self.killerNum,
                                  replace=False)
        return(killer)

    def sampleXy(self):
        allXy = np.array([[x, y] for x in self.grid for y in self.grid])
        peopleXyIx = np.random.choice(np.r_[0:len(allXy)],
                                      self.peopleNum,
                                      replace=False)
        peopleXy = allXy[peopleXyIx]

        peopleXyDf = np.column_stack((self.people, peopleXy))
        peopleXyDf = pd.DataFrame(peopleXyDf)
        peopleXyDf.columns = ['people', 'X', 'Y']

        peopleXyDf['role'] = 'civil'
        # peopleXyDf['statue'] = 'live'
        peopleXyDf.loc[np.isin(
            peopleXyDf.people, self.killer), 'role'] = 'killer'
        return(peopleXy, peopleXyDf)

    def toMap(self, df, showMap=True):
        peopleMap = np.empty((self.gridNum, self.gridNum))
        peopleMap[:, :] = -999
        peopleMap = peopleMap.astype(object)
        for i in df.index:
            if df.loc[i, 'statue'] == 'killed by Killer':
                peopleMap[df.loc[i, 'X'],
                          df.loc[i, 'Y']] = str(int(df.loc[i, 'people']))+'K'
            elif df.loc[i, 'statue'] == 'killed by Police':
                peopleMap[df.loc[i, 'X'],
                          df.loc[i, 'Y']] = str(int(df.loc[i, 'people']))+'P'
            else:
                peopleMap[df.loc[i, 'X'],
                          df.loc[i, 'Y']] = int(df.loc[i, 'people'])
        peopleMap = pd.DataFrame(peopleMap)
        # peopleMap[np.isnan(peopleMap)] = -100
        # peopleMap = peopleMap.astype(int)
        # peopleMap[peopleMap == -100] = '·'
        peopleMap[peopleMap == -999] = '·'
        print(peopleMap)
        return(peopleMap)

    def createTb(self):
        tb = self.peopleXyDf
        killerX = tb.loc[tb.role == 'killer', 'X']
        killerY = tb.loc[tb.role == 'killer', 'Y']
        tb['dist'] = tb.apply(lambda x: (
            (x.X-killerX)**2+(x.Y-killerY)**2)**0.5, axis=1)
        tb['statue'] = 'live'
        tb['deadTime'] = np.nan
        # tb['killBy'] = np.nan
        return(tb)

    def killerKill(self, tb, killPeopleOneStep=1):
        if self.killerKind == 'Near':
            killer = KillerNear()
        elif self.killerKind == 'Far':
            killer = KillerFar()
        deaths = killer.kill(tb, killPeopleOneStep)
        return(deaths)

    def checkStatue(self, tb):
        killerDeath = tb.loc[tb.role == 'killer', 'statue'].str.cat() != 'live'
        allCivilDeath = ~np.any(tb.loc[tb.role == 'civil', 'statue'] == 'live')
        gameEnd = any([killerDeath, allCivilDeath])
        civilLive = np.sum(tb.loc[tb.role == 'civil', 'statue'] == 'live')
        return(killerDeath, allCivilDeath, gameEnd, civilLive)

    def killer_step(self, tb, time, civilLiveLast, verbose=True, plotMap=True):
        civilKillbyKiller = self.killerKill(tb)
        tb.loc[np.isin(tb.people, civilKillbyKiller),
               'statue'] = 'killed by Killer'
        tb.loc[np.isin(tb.people, civilKillbyKiller), 'deadTime'] = time
        if verbose:
            print("Killer Session : Time", time, ", Civil ",
                  civilKillbyKiller[0], 'Killed by Killer!')
        if plotMap:
            self.toMap(tb)
        killerDeath = self.checkStatue(tb)[1]
        return(tb, killerDeath)

    def human_step(self, tb, time, civilLiveLast):
        policeGuess = int(input('Who is Killer ?'))
        if policeGuess == -999:
            print("Human Police Session : Police Hold On, Next Step!")
        else:
            if tb.loc[tb.people == policeGuess, 'statue'].item() != 'live':
                print('Are You Sure You Want Identify the Dead Man As the Killer ???')
            else:
                tb.loc[tb.people == policeGuess, 'statue'] = 'killed by Police'
                tb.loc[tb.people == policeGuess, 'deadTime'] = time
                if policeGuess == self.killer[0]:
                    print("Human Police Session : Time", time, ", Killer ",
                          policeGuess, 'Killed by Police! He is Killer!')
                else:
                    print("Human Police Session : Time", time, ", Civil ",
                          policeGuess, 'Killed by Police! He is innocent!')
        time = time+1
        killerDeath, allCivilDeath, gameEnd, civilLiveNow = self.checkStatue(
            tb)
        # gym style: reward
        reward = civilLiveNow - civilLiveLast
        # gym style: done
        done = gameEnd
        # gym style: info
        info = {'time': time,
                'civilLive': civilLiveNow}
        return(tb, reward, done, info)

    def machine_step(self, policeGuess, tb, time, civilLiveLast):
        if policeGuess == -999:
            pass
        else:
            if tb.loc[tb.people == policeGuess, 'statue'].item() != 'live':
                pass
            else:
                tb.loc[tb.people == policeGuess, 'statue'] = 'killed by Police'
                tb.loc[tb.people == policeGuess, 'deadTime'] = time
                if policeGuess == self.killer[0]:
                    pass
                else:
                    pass
        time = time+1
        killerDeath, allCivilDeath, gameEnd, civilLiveNow = self.checkStatue(
            tb)
        # gym style: reward
        reward = civilLiveNow - civilLiveLast
        # gym style: done
        done = gameEnd
        # gym style: info
        info = {'time': time,
                'civilLive': civilLiveNow}
        return(tb, reward, done, info)

    def play(self, tb, mode='human'):
        time = 0
        totalReward = 0
        done = False
        civilLiveLast = self.civilNum
        if mode == 'human':
            while not done:
                time = time+1
                tb, killerDeath = self.killer_step(tb, time, civilLiveLast)
                tb, reward, done, info = self. human_step(
                    tb, time, civilLiveLast)
                totalReward = totalReward+reward
                civilLiveLast = info.get('civilLive')
        return(tb, totalReward)


# %% Machine police

# random police


def randomPolice(tb):
    guess = np.random.choice(
        np.r_[-999, tb.people[tb.statue == 'live']])

    return(guess)

# near police


def nearPolice(tb):
    tbl = copy.deepcopy(tb.loc[tb.statue == 'live', :])
    tbl['distSum'] = 0
    tbk = copy.deepcopy(tb.loc[tb.statue == 'killed by Killer', :])
    ixL = tbl.index
    ixK = tbk.index
    for i in ixL:
        x = tbl.X[i]
        y = tbl.Y[i]
        for j in ixK:
            tbl.loc[i, 'distSum'] = tbl.loc[i, 'distSum'] + \
                ((x-tbk.X[j])**2+(y-tbk.Y[j])**2)**0.5
    # guess = tbp.people[tbp.distSum == np.min(tbp.distSum)].item()
    guess = tbl.loc[tbl.distSum == np.min(tbl.distSum), 'people'].values[0]
    return(guess)

# far police


def farPolice(tb):
    tbl = copy.deepcopy(tb.loc[tb.statue == 'live', :])
    tbl['distSum'] = 0
    tbk = copy.deepcopy(tb.loc[tb.statue == 'killed by Killer', :])
    ixL = tbl.index
    ixK = tbk.index
    for i in ixL:
        x = tbl.X[i]
        y = tbl.Y[i]
        for j in ixK:
            tbl.loc[i, 'distSum'] = tbl.loc[i, 'distSum'] + \
                ((x-tbk.X[j])**2+(y-tbk.Y[j])**2)**0.5
    # guess = tbp.people[tbp.distSum == np.min(tbp.distSum)].item()
    guess = tbl.loc[tbl.distSum == np.max(tbl.distSum), 'people'].values[0]
    return(guess)


# %% Human play

'''
# inital
mg = MurderGame(gridNum=20,
                peopleNum=20,
                killerKind='Far')
tb = mg.createTb()
tbInit = copy.deepcopy(tb)
tbHuman, totalRewardHuman = mg.play(tb)
'''

# %% Machine play

mg = MurderGame(gridNum=20,
                peopleNum=50,
                killerKind='Near')
rdnLst = []
nearLst = []
farLst = []

for i in np.r_[0:100]:
    tbRaw = mg.createTb()
    # random
    tb = copy.deepcopy(tbRaw)
    time = 0
    totalRewardMachine = 0
    done = False
    civilLiveLast = mg.civilNum
    while not done:
        time = time+1
        tb, killerDeath = mg.killer_step(tb, time, civilLiveLast, False, False)
        # tb, reward, done, info = mg. human_step(
        #     tb, time, civilLiveLast)
        policeGuess = randomPolice(tb)
        tb, reward, done, info = mg.machine_step(
            policeGuess, tb, time, civilLiveLast)
        totalRewardMachine = totalRewardMachine+reward
        civilLiveLast = info.get('civilLive')
    showScore = 1+(totalRewardMachine/mg.civilNum)
    rdnLst.append(showScore)
    # Near
    tb = copy.deepcopy(tbRaw)
    time = 0
    totalRewardMachine = 0
    done = False
    civilLiveLast = mg.civilNum
    while not done:
        time = time+1
        tb, killerDeath = mg.killer_step(tb, time, civilLiveLast, False, False)
        # tb, reward, done, info = mg. human_step(
        #     tb, time, civilLiveLast)
        policeGuess = nearPolice(tb)
        tb, reward, done, info = mg.machine_step(
            policeGuess, tb, time, civilLiveLast)
        totalRewardMachine = totalRewardMachine+reward
        civilLiveLast = info.get('civilLive')
    showScore = 1+(totalRewardMachine/mg.civilNum)
    nearLst.append(showScore)
    # Far
    tb = copy.deepcopy(tbRaw)
    time = 0
    totalRewardMachine = 0
    done = False
    civilLiveLast = mg.civilNum
    while not done:
        time = time+1
        tb, killerDeath = mg.killer_step(tb, time, civilLiveLast, False, False)
        # tb, reward, done, info = mg. human_step(
        #     tb, time, civilLiveLast)
        policeGuess = farPolice(tb)
        tb, reward, done, info = mg.machine_step(
            policeGuess, tb, time, civilLiveLast)
        totalRewardMachine = totalRewardMachine+reward
        civilLiveLast = info.get('civilLive')
    showScore = 1+(totalRewardMachine/mg.civilNum)
    farLst.append(showScore)


hist_data = [rdnLst, nearLst, farLst]

group_labels = ['Random', 'Near', 'Far']
colors = ['#333F44', '#37AA9C', '#94F3E4']

# Create distplot with curve_type set to 'normal'
fig = ff.create_distplot(hist_data, group_labels,
                         show_hist=False, colors=colors)
plot(fig)

random = np.mean(rdnLst)
near = np.mean(nearLst)
far = np.mean(farLst)
print(random,near,far)