# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 18:38:55 2015

@author: evansmothers
"""
import pandas as pd
import os
import re
import Dicts
import MyFunctions
import MachineLearning
import DataCollection
from sklearn import linear_model

    
    
''' Import csv of daily games '''
full_path = os.path.expanduser('~/Downloads/FanDuel-NBA-2016-12-01-17147-players-list.csv')
todayscsv = pd.read_csv(full_path)
yesterdaybool = False
yesterdayboolnew = False
dfbool = True
dfboolnew = True
firstofdaybool = True

''' Form list of player names'''
players = todayscsv["First Name"] + " " + todayscsv["Last Name"]

''' Append likely basketball-reference URL to player list  '''
lnlength = [len(todayscsv["Last Name"][i]) \
for i in range(len(todayscsv["Last Name"]))]
lnlength = [min(term,5) for term in lnlength]
players = [[i,players[i], "http://www.basketball-reference.com/players/" + \
re.sub(r'\W+', '',str(todayscsv["Last Name"][i]))[0].lower() + "/" + \
re.sub(r'\W+', '',str(todayscsv["Last Name"][i]))[0:lnlength[i]].lower() + \
re.sub(r'\W+', '',str(todayscsv["First Name"][i]))[0:2].lower() + "01"] \
for i in range(len(lnlength)) if \
MyFunctions.IsInjured(players[i],i,todayscsv) == 3]
    

''' Get correct URLs, home/away, opponent, days off (???) '''
players = [[player[0],player[1],MyFunctions.CorrectURL(player[1],player[2],\
Dicts.exceptions),todayscsv["Opponent"][player[0]], \
MyFunctions.HomeorAway(player[0],todayscsv), \
todayscsv["Position"][player[0]],todayscsv["Salary"][player[0]],\
todayscsv["Team"][player[0]]] for player in players]

''' Run function to get dataframe for paces of all teams '''
df4 = DataCollection.GetPace()

''' Run function to get defensive splits '''
defsplits = DataCollection.GetDefensiveSplits()

''' Run function to get weighted lines and over/unders for day's games '''
[adjustedlinedict,adjustedoverunderdict] = DataCollection.GoToVegas(todayscsv)

''' Run function to obtain team depthcharts '''
depthcharts = DataCollection.GetDepthCharts()

''' Create full list of players to check depth charts for injuries '''
playersfull = []
for i in range(len(todayscsv)):
    playersfull += [i,todayscsv["First Name"][i] + ' ' + \
    todayscsv["Last Name"][i]]

''' Run function to get last 5 games minutes average '''
minutesdict = DataCollection.GetMinutesDict(todayscsv)    

''' Call function to determine date-based names to save files '''
[todayfilename,yesterdayfilename] = DataCollection.GetFileNames()


''' Calculate expected score for a specific player '''
j = 6
playerexpectedscore = MyFunctions.ExpectedScore(players[j][0],players[j][1],players[j][2], \
players[j][3], players[j][4], df4, \
defsplits[Dicts.positions.index(players[j][5])],\
adjustedlinedict[Dicts.teams[Dicts.abbreviations[players[j][7]]]],\
depthcharts[players[j][7]],players[j][5],todayscsv,playersfull,minutesdict, \
adjustedoverunderdict[Dicts.teams[Dicts.abbreviations[players[j][7]]]], \
yesterdayfilename,todayfilename,df4)

''' Get all stats for all players '''
playerscore = {player[1]: MyFunctions.ExpectedScore(player[0],player[1],player[2],\
player[3],player[4],df4,defsplits[Dicts.positions.index(player[5])], \
adjustedlinedict[Dicts.teams[Dicts.abbreviations[player[7]]]], \
depthcharts[player[7]],player[5],todayscsv,playersfull,minutesdict,\
adjustedoverunderdict[Dicts.teams[Dicts.abbreviations[player[7]]]], \
yesterdayfilename,todayfilename,df4) for player in players}
               
''' OTHER DEFSPLITS VERSION HERE '''
#''' Calculate expected score for a specific player '''
#j = 30
#playerexpectedscore = MyFunctions.ExpectedScore(players[j][0],players[j][1],players[j][2], \
#players[j][3], players[j][4], df4, \
#defsplits[players[j][5]],\
#adjustedlinedict[Dicts.teams[Dicts.abbreviations[players[j][7]]]],\
#depthcharts[players[j][7]],players[j][5],todayscsv,playersfull,minutesdict, \
#adjustedoverunderdict[Dicts.teams[Dicts.abbreviations[players[j][7]]]], \
#yesterdayfilename,todayfilename,df4)
#
#''' Get all stats for all players '''
#playerscore = {player[1]: MyFunctions.ExpectedScore(player[0],player[1],player[2],\
#player[3],player[4],df4,defsplits[player[5]], \
#adjustedlinedict[Dicts.teams[Dicts.abbreviations[player[7]]]], \
#depthcharts[player[7]],player[5],todayscsv,playersfull,minutesdict,\
#adjustedoverunderdict[Dicts.teams[Dicts.abbreviations[player[7]]]], \
#yesterdayfilename,todayfilename,df4) for player in players}


expectedscore = [['Play?','Name','Position','Team','Salary','EFV',\
'EFV/Cost']] + [[0,player[1],player[5], \
str(player[7]),str(player[6]),str(playerscore[player[1]][-1]),\
str(playerscore[player[1]][-1]/player[6]*1000)] for player in players]

''' Split player stats into features for FPPM and min '''
fppmfeatures = {player: playerscore[player][0][0] for player in playerscore \
                if playerscore[player][0][1][5] != 0}
minfeatures = {player: playerscore[player][0][1] for player in playerscore \
               if playerscore[player][0][1][5] != 0}

''' Create headers for each set of features and responses '''
fppmheaders = ['Season','Last 10','H/A','Days Off','Opponent','Pace', \
'Position Defense','Over/Under','FPPM']
minheaders = ['Season','Last 10', 'H/A', 'Days Off', 'Opponent', \
'Rank','Rotation Binary','Injury','Adjacent Injury','Adjusted Line','Min']

''' Create df from today's player stats '''
fppmdfX = pd.DataFrame.from_dict(fppmfeatures,orient='index')
fppmdfX.columns = fppmheaders[:-1]
mindfX = pd.DataFrame.from_dict(minfeatures,orient='index')
mindfX.columns = minheaders[:-1]

''' Export day's feature variables with function call '''
MachineLearning.ExportFeatureVariables(fppmdfX,mindfX,todayfilename)

''' Form dictionary of player names with salaries for sorting purposes '''
salarydict = {player[1]: player[6] for player in players}

''' Save today's salary dictionary to file, load yesterday's if it exists '''
yesterdaysalarydict = MachineLearning.GetYesterdaySalaryDict(salarydict,\
                      todayfilename,yesterdayfilename,yesterdayboolnew)

''' If program ran yesterday, form df's 
containing features/responses with function call '''
[yesterdayfppmfull,yesterdayminfull,yesterdayfpfull] = \
MachineLearning.GetYesterdaysDF(yesterdayfilename,yesterdaybool,\
                                yesterdayboolnew,yesterdaysalarydict)

''' Get full dataframes via function call '''
[fppmdffull,mindffull,fpdffull] = MachineLearning.GetFullDF\
(yesterdayfppmfull,yesterdayminfull,yesterdayfpfull,dfbool,firstofdaybool,\
 dfboolnew)

''' Remove irrelevant early-season data '''
fppmdffull = pd.concat([fppmdffull[:3000],fppmdffull[4200:]])      
mindffull = pd.concat([mindffull[:3000],mindffull[4200:]])    
fpdffull = fpdffull[1000:]

''' Call function to set lower bounds for permissible data '''
[fppmdffull,mindffull] = MachineLearning.SetCutoff\
(fppmdffull,mindffull,0.6,18)

''' Split full dataframes into feature and response variables '''
fppmdffullX = fppmdffull.loc[:,fppmheaders[:-1]]
fppmdffullY = fppmdffull.loc[:,['FPPM']]
mindffullX = mindffull.loc[:,minheaders[:-1]]  
mindffullY = mindffull.loc[:,['Min']]

''' Select only relevant columns for FPPM linear regression '''
relevantcolumns = ['Season','Last 10','H/A','Days Off','Opponent', \
'Position Defense']
fppmdffullXactual = fppmdffullX[relevantcolumns]
fppmdfXactual = fppmdfX[relevantcolumns]

''' Form linear regression model and fit for fppm predicitons with function '''
fppmpredictions = MachineLearning.DoRegression\
(fppmdffullXactual,fppmdffullY,fppmdfXactual,True,0)

#''' Form linear regression model using fppmdffull '''
#fppmregr = linear_model.LinearRegression()
#fppmregr.fit(fppmdffullXactual,fppmdffullY)
#
#''' Use model to make predictions on today's data '''
#fppmpredictions = fppmregr.predict(fppmdfXactual)

''' Create list of player names from pandas df indices '''    
playernamelist = fppmdfX.index.tolist()

''' Form dictionary with player names and projected FPPM '''
FPPMdict = {playernamelist[i]: fppmpredictions[i].tolist() \
for i in range(len(playernamelist))}
    
''' Create new minutes df of rows unaffected by injuries, adjusted line '''
noinjurymindf = mindffull[mindffull['Injury'] + \
mindffull['Adjacent Injury'] == 0]
noinjurynolinemindf = noinjurymindf[abs(noinjurymindf['Adjusted Line']) < 1]
basemincolumns = ['Season','Last 10', 'H/A', 'Days Off', \
'Opponent']
basemindfX = noinjurynolinemindf[basemincolumns]
basemindfY = noinjurynolinemindf[['Min']]

''' Today's basemin feature variables '''
todaysbasemindfX = mindfX[basemincolumns]    

''' Make base minutes prediction for full dataframe and today's dataframe '''
fullbasemin = MachineLearning.DoRegression\
(basemindfX,basemindfY,mindffull[basemincolumns],True,0)
baseminpredictions = MachineLearning.DoRegression\
(basemindfX,basemindfY,todaysbasemindfX,True,0)
         
''' Create dictionary of today's players and basemin predictions '''    
basemindict = {playernamelist[i]:baseminpredictions[i].tolist() \
for i in range(len(playernamelist))}

''' Define columns for minutes adjustments '''
minerrorfeatures = ['Injury','Adjacent Injury','Adjusted Line']
minerrorresponses = ['Min Error']    

''' Create dataframe to calculate change from basemin based on line ''' 
minerror = mindffull.Min-fullbasemin.reshape(1,-1).tolist()[0]
fullminerrordf = mindffull
fullminerrordf['Min Error'] = minerror

''' Predict today's min error using function call '''
[todaysminerrordffull,optimalnneighbors] = MachineLearning.GetMinError\
(fullminerrordf,mindfX,minerrorfeatures,minerrorresponses,100)

''' Form dictionary of minutes error predictions '''
minerrordict = {playernamelist[i]:\
todaysminerrordffull.loc[[i]].values.tolist() \
for i in todaysminerrordffull.index.get_values().tolist()}

''' Form dictionary of expected minutes predictions '''
minpredict = {player: basemindict[player][0] + \
minerrordict[player][0][0] for player in minerrordict}

''' Form dictionary of expected fantasy value '''
FPpredict = {player: minpredict[player]*FPPMdict[player][0] \
for player in minerrordict} 

''' Create dictionary for player lookup '''
playerindexdict = {player[1]: [player[0],player[5],player[7],player[6]] \
for player in players}  

''' Create another list with machine learning projections to export '''
MLexpectedscore = [['Play?','Name','Position','Team','Salary','EFV',\
'EFV/Cost']] + [[0,player,playerindexdict[player][1],\
str(playerindexdict[player][2]),str(playerindexdict[player][3]),\
str(FPpredict[player]),\
str(FPpredict[player]/playerindexdict[player][3]*1000)] \
for player in playernamelist if player in FPpredict.keys()]  


''' Determine optimal model from available choices via function call '''
[bestmodelvec,newfppmheaders,newminheaders] = \
MachineLearning.ChooseModel(fpdffull)



''' Run alternative model and export results to CSV via function call '''
FPpredictnew = MachineLearning.RunNewModel(playernamelist,fpdffull,fppmdfX,mindfX,newfppmheaders,newminheaders,\
                            bestmodelvec[0],bestmodelvec[1],\
                            bestmodelvec[2],bestmodelvec[3],bestmodelvec[4])

MLexpectedscorenew = [['Play?','Name','Position','Team','Salary','EFV',\
'EFV/Cost']] + [[0,player,playerindexdict[player][1],\
str(playerindexdict[player][2]),str(playerindexdict[player][3]),\
str(FPpredictnew[player]),\
str(FPpredictnew[player]/playerindexdict[player][3]*1000)] \
for player in playernamelist if player in FPpredictnew.keys()]


''' Export regular and machine learning projections to CSV with function'''
MachineLearning.ExportProjectionsToCSV\
(todayfilename,expectedscore,MLexpectedscore,MLexpectedscorenew)


#############################################################################

