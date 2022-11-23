import pandas as pd
import numpy as np

class MurderGame():

    def __init__(self,
                 gridNum=4,
                 peopleNum=3,
                 killerNum=1):
        self.gridNum = gridNum
        self.grid = np.r_[0:gridNum]
        self.peopleNum = peopleNum
        self.killerNum = killerNum
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
            if df.loc[i, 'statue'] == 'kill by Killer':
                peopleMap[df.loc[i, 'X'],
                          df.loc[i, 'Y']] = str(int(df.loc[i, 'people']))+'K'
            elif df.loc[i, 'statue'] == 'kill by Police':
                peopleMap[df.loc[i, 'X'],
                          df.loc[i, 'Y']] = str(int(df.loc[i, 'people']))+'P'
            else:
                peopleMap[df.loc[i, 'X'],
                          df.loc[i, 'Y']] = int(df.loc[i, 'people'])
        peopleMap = pd.DataFrame(peopleMap)
        #peopleMap[np.isnan(peopleMap)] = -100
        #peopleMap = peopleMap.astype(int)
        #peopleMap[peopleMap == -100] = '·'
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
        #tb['killBy'] = np.nan
        return(tb)

    def killerRandomKill(self, tb, killPeopleOneStep=1):
        tobeKill = np.logical_and(tb.role == 'civil', tb.statue == 'live')
        distTobeKillRecip = 1/tb.dist[tobeKill]
        peopleTobeKill = tb.people[tobeKill]
        probTobeKill = distTobeKillRecip/np.sum(distTobeKillRecip)
        deaths = np.random.choice(peopleTobeKill,
                                  size=killPeopleOneStep,
                                  p=probTobeKill,
                                  replace=False)
        return(deaths)

    def checkStatue(self, tb):
        killerDeath = tb.loc[tb.role == 'killer', 'statue'].str.cat() != 'live'
        allCivilDeath = ~np.any(tb.loc[tb.role == 'civil', 'statue'] == 'live')
        gameEnd = any([killerDeath, allCivilDeath])
        civilLive = np.sum(tb.loc[tb.role == 'civil', 'statue'] == 'live')
        return(killerDeath, allCivilDeath, gameEnd, civilLive)

    def human_step(self, tb, time, civilLiveLast):
        civilKillbyKiller = self.killerRandomKill(tb)
        tb.loc[np.isin(tb.people, civilKillbyKiller),
               'statue'] = 'kill by Killer'
        tb.loc[np.isin(tb.people, civilKillbyKiller), 'deadTime'] = time
        print("Killer Session : Time", time, ", Civil ",
              civilKillbyKiller[0], 'Kill by Killer!')
        self.toMap(tb)
        if self.checkStatue(tb)[1]:
            pass
        else:
            policeGuess = int(input('Who is Killer ?'))
            if policeGuess == -999:
                print("Human Police Session : Police Hold On, Next Step!")
            else:
                tb.loc[tb.people == policeGuess,
                       'statue'] = 'kill by Police'
                tb.loc[tb.people == policeGuess, 'deadTime'] = time
                if policeGuess == self.killer[0]:
                    print("Human Police Session : Time", time, ", Killer ",
                          policeGuess, 'Kill by Police! He is Killer!')
                else:
                    print("Human Police Session : Time", time, ", Civil ", policeGuess,
                          'Kill by Police! He is innocent!')
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
        civilKillbyKiller = self.killerRandomKill(tb)
        tb.loc[np.isin(tb.people, civilKillbyKiller),
               'statue'] = 'kill by Killer'
        tb.loc[np.isin(tb.people, civilKillbyKiller), 'deadTime'] = time
        print("Killer Session : Time", time, ", Civil ",
              civilKillbyKiller[0], 'Kill by Killer!')
        self.toMap(tb)
        if self.checkStatue(tb)[1]:
            pass
        else:
            if policeGuess == -999:
                print("Machine Police Session : Police Hold On, Next Step!")
            else:
                tb.loc[tb.people == policeGuess,
                       'statue'] = 'kill by Police'
                tb.loc[tb.people == policeGuess, 'deadTime'] = time
                if policeGuess == self.killer[0]:
                    print("Machine Police Session : Time", time, ", Killer ",
                          policeGuess, 'Kill by Police! He is Killer!')
                else:
                    print("Machine Police Session : Time", time, ", Civil ", policeGuess,
                          'Kill by Police! He is innocent!')
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
                tb, reward, done, info = self. human_step(
                    tb, time, civilLiveLast)
                totalReward = totalReward+reward
                civilLiveLast = info.get('civilLive')
        return(tb, totalReward)



