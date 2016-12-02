# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 12:11:17 2016

@author: evansmothers
"""

import pandas as pd
from bs4 import BeautifulSoup
import urllib
import numpy
import Dicts
from datetime import date
import time


###############################EXPECTEDSCORE################################

''' Function to compute expected fantasy score of a player '''
def ExpectedScore(i,player,url,oppabb,homeaway,pace,posdef,adjustedline,\
depthchart,position,todayscsv,playersfull,minutesdict,adjustedoverunder,\
yesterdayfilename,todayfilename,df4):
    
    IsPlayoffs = False    
    
    ''' Get opponent name '''
    opponent = Dicts.abbreviations[oppabb]
    
    ''' Retrieve data frame from SALTS '''
    [seasonstatspm,lasttenstatspm,df,seasonavgs,lasttenavgs] = \
    SeasonAverageandLastTenScore(i,player,url,oppabb,\
    homeaway,pace,posdef,IsPlayoffs)

    ''' Function call to compute splits '''
    [hastatspm,daysoffstatspm,opponentstatspm,df2,df3,hastats,daysoffstats,\
    opponentstats]\
    = SplitsScores(i,player,url,oppabb,homeaway,pace,posdef,df, \
    IsPlayoffs)
    
    ''' If any splits are zero, replace with season averages '''
    if hastatspm == [0] * 7:
        hastatspm = seasonstatspm
    if daysoffstatspm == [0] * 7:
        daysoffstatspm = seasonstatspm
    if opponentstatspm == [0] * 7:
        opponentstatspm = seasonstatspm
    
    ''' Calculate opponent's pace and relative pace '''
    opponentlong = Dicts.teams[opponent]
    opponentpace = float(df4[df4["TEAM"] == opponent]["PACE"])
    meanpace = numpy.mean([float(element) for element in df4.PACE])
    relativepace = opponentpace/meanpace
    adjustedpace = relativepace - 1

    
    ''' Alternative defsplits '''
    opponentposdef = float(posdef[posdef["Team"] == oppabb]["FDG"])
    relativeposdef = opponentposdef/numpy.mean(posdef.FDG)
    adjustedposdef = (opponentposdef - numpy.mean(posdef.FDG))/\
    numpy.mean(posdef.FDG)
    
#    REGULAR DEFSPLITS
#    ''' Calculate opponent's position defense and relative position defense '''
#    opponentposdef = float(posdef[posdef["Team"] == opponentlong]["Season"]) 
#    relativeposdef = opponentposdef/numpy.mean(posdef.Season)
#    adjustedposdef = (opponentposdef-numpy.mean(posdef.Season))/\
#    numpy.mean(posdef.Season)
    
    ''' Average of relative pace and relative position defense '''
    ''' weightfactor = numpy.mean([relativepace,relativeposdef]) '''
    
    ''' Parameters for expected fantasy value '''
    a = [1/3,1/3,1/9,1/9,1/9]
    ''' a = [1/6,1/2,1/9,1/9,1/9] '''
    ''' a = [0.2,0.2,0.2,0.2,0.2] '''
    
    ''' Base minutes parameter vector '''
    b = [1/3,1/3,1/9,1/9,1/9]
    ''' b = [0.3,0.5,0,0.15,0.05] '''   
    
    ''' Calculate base value for expected minutes '''
    baseminutes = b[0]*seasonstatspm[6]+b[1]*lasttenstatspm[6]\
    +b[2]*hastatspm[6]+b[3]*daysoffstatspm[6]+b[4]*opponentstatspm[6]

           
    ''' Calculate expected number of minutes played for player '''
    [expectedminutes,injuryinfo] = ExpectedMinutes(baseminutes,player,\
    position,depthchart,adjustedline,todayscsv,playersfull,minutesdict)    
        
    
    ''' Create vector of all possible relevant info'''
    datavec = [CalculateScore(seasonstatspm[:6]),seasonavgs[6], \
    CalculateScore(lasttenstatspm[:6]), lasttenavgs[7], \
    CalculateScore(hastatspm[:6]),hastats[6], \
    CalculateScore(daysoffstatspm[:6]),daysoffstats[6], \
    CalculateScore(opponentstatspm[:6]), opponentstats[6], \
    adjustedpace,adjustedposdef,adjustedoverunder,adjustedline,injuryinfo]
    fantasyvec = [datavec[i] for i in range(0,10,2)]
    manyminvec = [datavec[i] for i in range(1,11,2)]    
    
    ''' Adjust for any missing data '''
    for k in range(len(fantasyvec)):
        if fantasyvec[k] == 0:
            for j in range(5):
                if j != k:
                    a[j] += a[k]/4
            a[k] = 0
    
    expectedfppm = a[0]*fantasyvec[0] + a[1]*fantasyvec[1] + \
    a[2] * fantasyvec[2] + a[3] * fantasyvec[3] + a[4] * fantasyvec[4]       
      
    ''' Split into two vectors for predicting FPPM and minutes '''
    ppmvec = fantasyvec + [adjustedpace,adjustedposdef,adjustedoverunder]
    minvec = manyminvec + injuryinfo + [adjustedline]
    featurevec = [ppmvec,minvec]

    ''' Calculate expected fantasy value from expected minutes and FPPM '''    
    expectedvalue = expectedminutes * expectedfppm
    
    ''' Account for average between pace and position defense '''
    weightfactor = relativeposdef
    expectedvalue *= weightfactor
        
    ''' Return tons of info '''
    return [featurevec,expectedvalue]

################################CALCULATESCORE##############################

''' Calculate fantasy score of a player vector '''
def CalculateScore(player):
    points = player[0]
    rebounds = player[1]
    assists = player[2]
    blocks = player[3]
    steals = player[4]
    turnovers = player[5]
    return points + 1.2*rebounds + 1.5*assists +\
    2*(blocks + steals) - turnovers

###################################CLEAN####################################
    
''' Clean up entries in depth chart '''
def Clean(entry):
    if entry == '\xa0':
        return ''
    newentry = entry.replace('\n','')
    newerentry = newentry.replace('#','')
    newestentry = ''.join([char for char in newerentry if not char.isdigit()])
    if newestentry == 'Maybyner Nene':
        return 'Nene Hilario'
    return newestentry
    
#################################CORRECTURL#################################

''' Function to correct any incorrect URLs '''
def CorrectURL(playername,playerurl,exceptions):
    if playername in exceptions.keys():
        return exceptions[playername]
    return playerurl
    
#################################HOMEORAWAY#################################

''' Function to determine whether game is home or away ''' 
def HomeorAway(i,todayscsv):
    if todayscsv["Game"][i][0:len(todayscsv["Team"][i])] == todayscsv["Team"][i]:
        return "Road"
    return "Home"
    
###################################SALTS####################################
    
''' Calculate season average and last ten fantasy scores '''    
def SeasonAverageandLastTenScore(i,player,url,oppabb,homeaway,pace,posdef,\
IsPlayoffs):    
    
    if IsPlayoffs:
        url1 = url + "/gamelog/2017/"
        page = urllib.request.urlopen(url1) 
        soup = BeautifulSoup(page.read(),"lxml")
        
        ''' Regular season stats '''
        seasontable = soup.find("table", attrs = \
        {"class": "sortable row_summable stats_table"})
        column_headers = [th.getText() for th in \
        seasontable.findAll("tr",limit=1)[0].findAll("th")]
        season_data_rows = seasontable.findAll("tr")[1:]
        season_player_data = [[td.getText() for td in \
        season_data_rows[i].findAll("td")] \
        for i in range(len(season_data_rows))]
        seasondf = pd.DataFrame(season_player_data,columns=column_headers)        
        
        ''' Remove empty rows (DNP) '''
        seasondf = seasondf[seasondf.PTS.notnull()]
    
    
        ''' Convert appropriate columns to float '''
        seasondf.PTS = seasondf.PTS.astype("float")
        seasondf.TRB = seasondf.TRB.astype("float")
        seasondf.AST = seasondf.AST.astype("float")
        seasondf.BLK = seasondf.BLK.astype("float")
        seasondf.STL = seasondf.STL.astype("float")
        seasondf.TOV = seasondf.TOV.astype("float")
        seasondf.G = seasondf.G.astype("int")
    
        ''' Convert minutes column to float '''
        seasondf['MP'] = seasondf['MP'].apply(lambda x: float(str(x[:x.index(':')]))\
        + float(str(x[x.index(':')+1:]))/60)        
        
        
        ''' Playoff stats '''
        playofftable = soup.find("table", attrs = \
        {"class": "sortable row_summable stats_table", \
        "id": "pgl_basic_playoffs"})
        playoff_data_rows = playofftable.findAll("tr")[1:]
        playoff_player_data = [[td.getText() for td in \
        playoff_data_rows[i].findAll("td")] \
        for i in range(len(playoff_data_rows))]
        playoffdf = pd.DataFrame(playoff_player_data,columns=column_headers)
        
        ''' Remove empty rows (DNP) '''
        playoffdf = playoffdf[playoffdf.PTS.notnull()]
    
        ''' Games played during season '''
        seasongamesplayed = max(seasondf.G)
    
        ''' Convert appropriate columns to float '''
        playoffdf.PTS = playoffdf.PTS.astype("float")
        playoffdf.TRB = playoffdf.TRB.astype("float")
        playoffdf.AST = playoffdf.AST.astype("float")
        playoffdf.BLK = playoffdf.BLK.astype("float")
        playoffdf.STL = playoffdf.STL.astype("float")
        playoffdf.TOV = playoffdf.TOV.astype("float")
        playoffdf.G = playoffdf.G.astype("int")
    
        ''' Convert minutes column to float '''
        playoffdf['MP'] = playoffdf['MP'].apply(lambda x: float(str(x[:x.index(':')]))\
        + float(str(x[x.index(':')+1:]))/60) 
        
        ''' Adjust games column of playoff dataframe '''
        playoffdf['G'] = playoffdf['G'].apply(lambda x: x+seasongamesplayed)
        
        ''' Merge regular season and playoffs into single dataframe '''
        df = seasondf.append(playoffdf)
        
    else:    
        url1 = url + "/gamelog/2017/"
        page = urllib.request.urlopen(url1)
        soup = BeautifulSoup(page.read(),"lxml")
        table = soup.find("table",attrs = \
        {"class": "row_summable sortable stats_table"})
        column_headers = [th.getText() for th in \
        table.findAll("tr",limit=1)[0].findAll("th")[1:]]
        data_rows = table.findAll("tr")[1:]    
        player_data = [[td.getText() for td in \
        data_rows[i].findAll("td")] for i in range(len(data_rows))]
        
        ''' IF INSUFFICIENT DATA, RETURN ALL ZEROS '''
        if max([len(player_data[i]) for i in range(0,len(player_data))]) \
               < len(column_headers):
               return [[0]*7,[0]*8,0,[0]*7,[0]*8]
        
        df = pd.DataFrame(player_data,columns=column_headers)
    
        ''' Remove empty rows (DNP) '''
        df = df[df.PTS.notnull()]
    
    
        ''' Convert appropriate columns to float '''
        df.PTS = df.PTS.astype("float")
        df.TRB = df.TRB.astype("float")
        df.AST = df.AST.astype("float")
        df.BLK = df.BLK.astype("float")
        df.STL = df.STL.astype("float")
        df.TOV = df.TOV.astype("float")
        df.G = df.G.astype("int")
    
        ''' Convert minutes column to float '''
        df['MP'] = df['MP'].apply(lambda x: float(str(x[:x.index(':')]))\
        + float(str(x[x.index(':')+1:]))/60)

    ''' Calculate season average '''
    seasonavgs = df[["PTS","TRB","AST","BLK","STL","TOV","MP"]].mean(axis=0)
    
    
    ''' Calculate season stats per minute '''
    seasonstatspm = [element/seasonavgs[6] \
    for element in seasonavgs[:6]] + [seasonavgs[6]]
            
    ''' Games played (for sample size) '''
    gamesplayed = max(df.G)
    seasonavgs = [element for element in seasonavgs] + [gamesplayed]
 
    ''' Calculate last n (n=5 or 10) average and corresponding fantasy points '''
    lastgame = len(df.PTS)
    goback = 5
    lasttenavgs = [numpy.mean(df.PTS.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.TRB.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.AST.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.BLK.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.STL.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.TOV.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.MP.iloc[lastgame-goback:lastgame]), \
    numpy.mean(df.MP.iloc[lastgame-5:lastgame])]
        
    ''' NOTE: FOR NOW THIS IS REALLY LAST 2 AVERAGES '''
    ''' Calculate last ten stats per minute '''
    lasttenstatspm = [element/lasttenavgs[6] \
        for element in lasttenavgs[:6]] + [lasttenavgs[6]] + [lasttenavgs[7]]
    
    print(player,"per minute season averages",seasonstatspm[:6])
    print(player, "last ten averages",lasttenstatspm[:6])    

    return [seasonstatspm,lasttenstatspm,df,seasonavgs,lasttenavgs]

##################################SPLITS####################################

''' Get splits per minute for a given player '''    
def SplitsScores(i,player,url,oppabb,homeaway,pace,posdef,df,IsPlayoffs):
    
    ''' Get regular opponent name '''
    opponent = Dicts.abbreviations[oppabb]    
    
    ''' Extract HTML table from 2017 splits, convert to data frame '''
    url2 = url + "/splits/2017/"
    page2 = urllib.request.urlopen(url2)
    soup2 = BeautifulSoup(page2.read(),"lxml")
    table2 = soup2.find("table",attrs = {"id": "splits"})
    column_headers2 = [th.getText() for th in \
    table2.findAll("tr",limit=2)[1].findAll("th")[1:]]
    data_rows2 = table2.findAll("tr")[1:]    
    player_data2 = [[td.getText() for td in \
    data_rows2[i].findAll("td")] for i in range(len(data_rows2))]
    df2 = pd.DataFrame(player_data2,columns=column_headers2)
    
    ''' Extract HTML table from 2016 splits, convert to data frame '''
    url3 = url + "/splits/2016/"
    page3 = urllib.request.urlopen(url3)
    soup3 = BeautifulSoup(page3.read(),"lxml")    
    table3 = soup3.find("table",attrs = {"id": "splits"})
    
    ''' Make sure table is nonempty '''
    if table3 != None:
        column_headers3 = [th.getText() for th in \
            table3.findAll("tr",limit=2)[1].findAll("th")[1:]]
        data_rows3 = table3.findAll("tr")[1:]    
        player_data3 = [[td.getText() for td in \
            data_rows3[i].findAll("td")] for i in range(len(data_rows3))]
        df3 = pd.DataFrame(player_data3,columns=column_headers3)
        

        '''Remove empty rows (DNP) '''
        df3 = df3[df3.G.notnull()]

        '''Convert appropriate columns to float: 2015 splits'''
        df3.PTS = df3.PTS.astype("float")
        df3.TRB = df3.TRB.astype("float")
        df3.AST = df3.AST.astype("float")
        df3.BLK = df3.BLK.astype("float")
        df3.STL = df3.STL.astype("float")
        df3.TOV = df3.TOV.astype("float")
        df3.MP = df3.MP.astype("float")
        df3.G = df3.G.astype("int")
        
        if any(df3.Value == opponent):
            opponentstatsprevious = \
            [float(df3[df3["Value"] == opponent]["PTS"].iloc[:,0]), \
            float(df3[df3["Value"] == opponent]["TRB"].iloc[:,0]), \
            float(df3[df3["Value"] == opponent]["AST"].iloc[:,0]), \
            float(df3[df3["Value"] == opponent]["BLK"]), \
            float(df3[df3["Value"] == opponent]["STL"]),\
            float(df3[df3["Value"] == opponent]["TOV"]),\
            float(df3[df3["Value"] == opponent]["MP"].iloc[:,0])]
            gamesold = float(df3[df3["Value"] == opponent]["G"])
        else:
            opponentstatsprevious = [0]*7
            gamesold = 0
    else:
        opponentstatsprevious = [0]*7
        gamesold = 0
        df3 = None
    
    '''Remove empty rows (DNP) '''
    df2 = df2[df2.G.notnull()]

    ''' Convert appropriate columns to float: 2016 splits '''
    df2.PTS = df2.PTS.astype("float")
    df2.TRB = df2.TRB.astype("float")
    df2.AST = df2.AST.astype("float")
    df2.BLK = df2.BLK.astype("float")
    df2.STL = df2.STL.astype("float")
    df2.TOV = df2.TOV.astype("float")
    df2.MP = df2.MP.astype("float")
    df2.G = df2.G.astype("int")
    
    '''Get H/A splits totals '''
    if any(df2.Value == homeaway):
        hastats = [float(df2[df2["Value"] == homeaway]["PTS"].iloc[:,0]), \
        float(df2[df2["Value"] == homeaway]["TRB"].iloc[:,0]), \
        float(df2[df2["Value"] == homeaway]["AST"].iloc[:,0]), \
        float(df2[df2["Value"] == homeaway]["BLK"]), \
        float(df2[df2["Value"] == homeaway]["STL"]), \
        float(df2[df2["Value"] == homeaway]["TOV"]), \
        float(df2[df2["Value"] == homeaway]["MP"].iloc[:,0])]

        ''' H/A splits averages '''
        hastats = [hastat/float(df2[df2["Value"] == homeaway]["G"]) for hastat \
        in hastats]
        
        ''' Convert to per minute stats '''
        hastatspm = [element/hastats[6] for element in hastats[:6]] \
        + [hastats[6]]
        
        ''' Add games to hastats '''
        hastats += [float(df2[df2["Value"] == homeaway]["G"])]
        
        ''' MODIFIED SECTION HERE (USE LAST YEAR'S SPLITS) '''   

    elif table3 != None and any(df3.Value == homeaway):
        hastats = [float(df3[df3["Value"] == homeaway]["PTS"].iloc[:,0]), \
        float(df3[df3["Value"] == homeaway]["TRB"].iloc[:,0]), \
        float(df3[df3["Value"] == homeaway]["AST"].iloc[:,0]), \
        float(df3[df3["Value"] == homeaway]["BLK"]), \
        float(df3[df3["Value"] == homeaway]["STL"]), \
        float(df3[df3["Value"] == homeaway]["TOV"]), \
        float(df3[df3["Value"] == homeaway]["MP"].iloc[:,0])]

        ''' H/A splits averages '''
        hastats = [hastat/float(df3[df3["Value"] == homeaway]["G"]) for hastat \
        in hastats]
        
        ''' Convert to per minute stats '''
        hastatspm = [element/hastats[6] for element in hastats[:6]] \
        + [hastats[6]]
        
        ''' Add games to hastats '''
        hastats += [float(df3[df3["Value"] == homeaway]["G"])]

    else:
        hastats = [0]*7
        hastatspm = [0]*7

        ''' END MODIFIED SECTION '''
        
        
    ''' Find out number of days off, create daysoff string '''
    currentgame = date(int(time.strftime("%Y")),int(time.strftime("%m")), \
    int(time.strftime("%d")))
    gamesplayed = len(df.G)
    lastgamestring = df[df["G"] == gamesplayed].Date.get_values()[0]
    previousgame = date(int(lastgamestring[0:4]),int(lastgamestring[5:7]),\
    int(lastgamestring[8:10]))
    daysoffint = int(str(currentgame - previousgame)[0]) - 1
    if daysoffint == 0 or daysoffint == 2:
        daysoff = str(daysoffint) + " Days"
    elif daysoffint == 1:
        daysoff = str(daysoffint) + " Day"
    else:
        daysoff = "3+ Days"
    
    
    '''Get days off splits totals'''
    if any(df2.Value == daysoff):
        daysoffstats = [float(df2[df2["Value"] == daysoff]["PTS"].iloc[:,0]), \
        float(df2[df2["Value"] == daysoff]["TRB"].iloc[:,0]), \
        float(df2[df2["Value"] == daysoff]["AST"].iloc[:,0]), \
        float(df2[df2["Value"] == daysoff]["BLK"]), \
        float(df2[df2["Value"] == daysoff]["STL"]), \
        float(df2[df2["Value"] == daysoff]["TOV"]), \
        float(df2[df2["Value"] == daysoff]["MP"].iloc[:,0])]

        ''' Days off splits averages and expected fantasy points '''
        daysoffstats = [daysoffstat/float(df2[df2["Value"] == daysoff]["G"]) \
        for daysoffstat in daysoffstats]
        
        if daysoffstats[6] != 0:
            ''' Convert to per minute stats '''
            daysoffstatspm = [element/daysoffstats[6] \
            for element in daysoffstats[:6]] + [daysoffstats[6]]
        else:
            daysoffstatspm = [0]*7
            daysoffstats = [0]*8
        
        ''' Add games to daysoffstats '''
        daysoffstats += [float(df2[df2["Value"] == daysoff]["G"])]
        
        ''' MODIFIED SECTION HERE (USE LAST YEAR'S STATS) '''
    elif table3 != None and any(df3.Value == daysoff):
        daysoffstats = [float(df3[df3["Value"] == daysoff]["PTS"].iloc[:,0]), \
        float(df3[df3["Value"] == daysoff]["TRB"].iloc[:,0]), \
        float(df3[df3["Value"] == daysoff]["AST"].iloc[:,0]), \
        float(df3[df3["Value"] == daysoff]["BLK"]), \
        float(df3[df3["Value"] == daysoff]["STL"]), \
        float(df3[df3["Value"] == daysoff]["TOV"]), \
        float(df3[df3["Value"] == daysoff]["MP"].iloc[:,0])]

        ''' Days off splits averages and expected fantasy points '''
        daysoffstats = [daysoffstat/float(df3[df3["Value"] == daysoff]["G"]) \
        for daysoffstat in daysoffstats]
        
        if daysoffstats[6] != 0:
            ''' Convert to per minute stats '''
            daysoffstatspm = [element/daysoffstats[6] \
            for element in daysoffstats[:6]] + [daysoffstats[6]]
        else:
            daysoffstatspm = [0]*7
            daysoffstats = [0]*8
        
        ''' Add games to daysoffstats '''
        daysoffstats += [float(df3[df3["Value"] == daysoff]["G"])]
    
    else:
        daysoffstatspm = [0]*7
        daysoffstats = [0]*8
    

        ''' END MODIFIED SECTION '''
        
   
    ''' Opponent splits averages and expected fantasy points ''' 
    if any(df2.Value == opponent):
        opponentstatscurrent = [float(df2[df2["Value"] == opponent]["PTS"].iloc[:,0]), \
        float(df2[df2["Value"] == opponent]["TRB"].iloc[:,0]), \
        float(df2[df2["Value"] == opponent]["AST"].iloc[:,0]), \
        float(df2[df2["Value"] == opponent]["BLK"]), \
        float(df2[df2["Value"] == opponent]["STL"]), \
        float(df2[df2["Value"] == opponent]["TOV"]), \
        float(df2[df2["Value"] == opponent]["MP"].iloc[:,0])]
        gamesnew = float(df2[df2["Value"] == opponent]["G"])
    else: 
        opponentstatscurrent = [0]*7
        gamesnew = 0

    opponentstats = [float(term) for term in numpy.sum([opponentstatsprevious, \
    opponentstatscurrent],axis = 0)] + [gamesnew+gamesold]
    if gamesnew + gamesold != 0:          
        if opponentstats[6] != 0:
            ''' Convert to per minute and per game stats '''    
            opponentstatspm = [element/opponentstats[6] \
            for element in opponentstats[:6]] + [opponentstats[6]/\
            (gamesnew+gamesold)]
            opponentstats = [element/opponentstats[7] for element in \
            opponentstats[:7]] + [opponentstats[7]]
        else:
            opponentstatspm = [0]*7
            opponentstats = [0]*8
    else:
        opponentstatspm = [0]*7
        opponentstats = [0]*8
        
    ''' Check for stats against opponent in this year's playoffs '''    
    if IsPlayoffs:
        url1 = url + "/gamelog/2016/"
        page = urllib.request.urlopen(url1) 
        soup = BeautifulSoup(page.read(),"lxml")
        playofftable = soup.find("table", attrs = \
        {"class": "sortable row_summable stats_table", \
        "id": "pgl_basic_playoffs"})
        column_headers = [th.getText() for th in \
        playofftable.findAll("tr",limit=1)[0].findAll("th")]
        playoff_data_rows = playofftable.findAll("tr")[1:]
        playoff_player_data = [[td.getText() for td in \
        playoff_data_rows[i].findAll("td")] \
        for i in range(len(playoff_data_rows))]
        playoffdf = pd.DataFrame(playoff_player_data,columns=column_headers)
        
        ''' Remove empty rows (DNP) '''
        playoffdf = playoffdf[playoffdf.PTS.notnull()]
    
        ''' Convert appropriate columns to float '''
        playoffdf.PTS = playoffdf.PTS.astype("float")
        playoffdf.TRB = playoffdf.TRB.astype("float")
        playoffdf.AST = playoffdf.AST.astype("float")
        playoffdf.BLK = playoffdf.BLK.astype("float")
        playoffdf.STL = playoffdf.STL.astype("float")
        playoffdf.TOV = playoffdf.TOV.astype("float")
        playoffdf.G = playoffdf.G.astype("int")
    
        ''' Convert minutes column to float '''
        playoffdf['MP'] = playoffdf['MP'].apply(lambda x: float(str(x[:x.index(':')]))\
        + float(str(x[x.index(':')+1:]))/60) 
        
        ''' Find all previous playoff games against current opponent '''
        playoffdf = playoffdf[playoffdf['Opp'].str.contains(oppabb)]
        
        ''' If there are previous games, add them to other opponent stats '''
        if not playoffdf.empty():
           playoffgames = len(playoffdf)
           totalgames = playoffgames+opponentstats[7]
           playoffstats = [sum(playoffdf.PTS),sum(playoffdf.TRB),\
           sum(playoffdf.AST),sum(playoffdf.BLK),sum(playoffdf.STL),\
           sum(playoffdf.TOV),sum(playoffdf.MP)] + [playoffgames]
           opponentstats = [((opponentstats[i]*opponentstats[7])+\
           playoffstats[i])/(opponentstats[7]+playoffstats[7]) \
           for i in range(len(playoffstats)-1)] + [totalgames]
           opponentstatspm = [opponentstats[i]/opponentstats[6] \
           for i in range(len(opponentstats)-1)] + [opponentstats[6]]
    
    print(player, "H/A stats per minute", hastatspm[:6])
    print(player,"Days off splits per minute",daysoffstatspm[:6])    
    print(player,"Opponent stats per minute", opponentstatspm[:6])
           

    return[hastatspm,daysoffstatspm,opponentstatspm,df2,df3,hastats,\
    daysoffstats,opponentstats]

#################################ISINJURED##################################
    
''' Determine if a given player is injured/useful '''
def IsInjured(player,i,todayscsv):
    if todayscsv["Injury Indicator"][i] == 'O':
        return 0
    if todayscsv["Injury Indicator"][i] == 'GTD':
        return 1
    if todayscsv["FPPG"][i] <= 7:
        return 2
    if todayscsv["Played"][i] >= 50:
        return 4
    return 3   

###################################IGNORE###################################
    
''' Determine whether to ignore a pair of players when considering injuries '''    
def Ignore(otherplayer, player, ignoredict):
    if otherplayer in ignoredict:
        if ignoredict[otherplayer] == player:
            return True
    return False

################################EXPECTEDMINUTES#############################
    
''' Calculate expected minutes for a given player '''    
def ExpectedMinutes(baseminutes,player,position,depthchart,adjustedline,todayscsv,
                    playersfull,minutesdict):
#    ''' Vectors of parameters to account for injury adjustments '''
#    starteradjust = {'2': 0.5, '3': 0.25, '4': 0.15}
#    secondadjust  = {'1': 0.3, '3': 0.35, '4': 0.25}
#    thirdadjust = {'1': 0.1, '2': 0.4, '4': 0.4}
#    scrubadjust = {'1': 0.05, '2': 0.2, '3': 0.35, '4': 0.3}
#    alladjustments = [starteradjust,secondadjust,thirdadjust,scrubadjust]  
    print(player,"baseminutes",baseminutes)
    
    ''' Waived players to ignore '''
    if player in Dicts.depthchartignore:
        return [baseminutes,[0]*4]
                
    ''' Injury adjustment vectors '''
    rotationvec = [0.2,0.3,0.2,0.1]
    limptvec = [0.2,0.1,0] 
    
    ''' Dictionary of injuries to ignore '''
    ignoredict = {}
                    
    ''' Vector of adjustment parameters for Vegas lines '''
    starteradjust2 = [1.2,0.8]
    secondadjust2 = [0.7,1.3]
    thirdadjust2 = [0.6,1.4]
    scrubadjust2 = [0.6,1.4]    
    lineadjustments = [starteradjust2,secondadjust2,thirdadjust2,scrubadjust2]                    
    
    ''' Set expected minutes at base value provided '''
    expectedminutes = baseminutes
    
    ''' Boolean to check that player appears in team's depth chart '''
    foundplayer = False    
    
    ''' Check to make sure player's name agrees with depth chart '''
    if player in Dicts.depthchartexceptions:
        player = Dicts.depthchartexceptions[player]

    ''' Total number of slots '''    
    chartlength = len(depthchart['Role'])    
    
    ''' Check number of starter/rotation player slots in depth chart '''
    maxrotationlength = sum([element == 'Starters' or element == 'Rotation' \
    for element in depthchart['Role']])    
    ''' Find player's position in depth chart '''    
    if player in depthchart[position]:
        playerspot = min(depthchart[position].index(player)+1,4)
        newposition = position
        foundplayer = True
    else:
        for key in depthchart:
            if player in depthchart[key]:
                playerspot = min(depthchart[key].index(player)+1,4)
                newposition = key
                foundplayer = True
                
    if player in Dicts.depthchartadjust.keys():
        playerspot = Dicts.depthchartadjust[player] 
    if not foundplayer:
        return [baseminutes,[0]*4]
    else:     
        ''' Determine if player is rotation or not '''
        if playerspot <= maxrotationlength:
            isrotation = True
        else:
            isrotation = False
        
        ''' Binary to export for whether a player is in the rotation '''
        if isrotation:
            rotationbin = 1
        else:
            rotationbin = 0
            
                
        
        ''' Create lists of rotation and non-rotation players at same position '''
        rotation = []
        limpt = []    
        for i in range(maxrotationlength):
            if depthchart[newposition] != '' and \
                depthchart[newposition][i] != player:
                rotation.append(depthchart[newposition][i])
        for i in range(maxrotationlength,chartlength):
            if depthchart[newposition][i] != '' and \
                depthchart[newposition][i] != player:
                    limpt.append(depthchart[newposition][i])
            
        ''' Check for injuries among rotation players at same position '''
        rotationinjuryct = [False]*len(rotation)
        makeupminutes = 0
        for i in range(len(rotation)):
            otherplayer = rotation[i]
            if otherplayer in playersfull and otherplayer in minutesdict.keys():
                otherstatus = IsInjured\
                (otherplayer,playersfull[playersfull.index(otherplayer)-1],todayscsv)
                if otherstatus == 0 \
                and not Ignore(player,otherplayer,ignoredict):
                    makeupminutes += minutesdict[otherplayer]
                    print('O: eligible (rotation)',otherplayer,minutesdict[otherplayer])
                    rotationinjuryct[i] = True
                if otherstatus == 1 \
                and not Ignore(player,otherplayer,ignoredict):
                    makeupminutes += minutesdict[otherplayer]/2
                    print('GTD: eligible (rotation)',otherplayer,minutesdict[otherplayer]/2)
                    rotationinjuryct[i] = True
            
        ''' Check for injuries among limpt players at same position '''       
        limptinjuryct = [False]*len(limpt)
        for i in range(len(limpt)):
            otherplayer = limpt[i]
            if otherplayer in playersfull and otherplayer in minutesdict.keys():
                otherstatus = IsInjured\
                (otherplayer,playersfull[playersfull.index(otherplayer)-1],todayscsv)
                if otherstatus == 0 \
                and not Ignore(player,otherplayer,ignoredict):
                    makeupminutes += minutesdict[otherplayer]
                    print('O: eligible (lim pt)',otherplayer,minutesdict[otherplayer])
                    limptinjuryct[i] = True
                if otherstatus == 1 \
                and not Ignore(player,otherplayer,ignoredict):
                    makeupminutes += minutesdict[otherplayer]/2
                    print('GTD: eligible (lim pt)',otherplayer,minutesdict[otherplayer]/2)
                    limptinjuryct[i] = True
    
    
    
    
        if isrotation:
            ''' rotation.insert(playerspot-1,player) '''
            rotationinjuryct.insert(playerspot-1,None)
            rotationinjuryct = [element for element in rotationinjuryct \
            if element != True]
            newplayerspot = rotationinjuryct.index(None) + 1 
            expectedminutes += rotationvec[newplayerspot-1]*makeupminutes
        elif playerspot == maxrotationlength+1:
            expectedminutes += limptvec[min(len(rotation)-1,2)]*makeupminutes
        
    ''' Adjust player's minutes based on adjusted spread '''
    if adjustedline < 0:
        expectedminutes *= 1 + \
        (((1-lineadjustments[playerspot-1][0])*adjustedline)/10)
    if adjustedline > 0:
        expectedminutes *= 1 + \
        (((lineadjustments[playerspot-1][1]-1)*adjustedline)/10)
    print(player,"adjusted line",adjustedline)
    
    ''' Get number of player's position in depth chart '''
    playerposnum = Dicts.posnum[newposition] 
    
    ''' Find adjacent positions '''
    if playerposnum == 5:
        tocheck = [Dicts.positions[3]]
    elif playerposnum == 1:
        tocheck = [Dicts.positions[1]]
    else:
        tocheck = [Dicts.positions[playerposnum],\
        Dicts.positions[playerposnum-2]]
    
    ''' Check for injuries in adjacent positions '''
    adjacentmakeupminutes = 0
    for position in tocheck:
        for otherplayer in depthchart[position]:
            if otherplayer in playersfull and otherplayer in minutesdict.keys():
                otherstatus = IsInjured(otherplayer,\
                playersfull[playersfull.index(otherplayer)-1],todayscsv)
                if otherstatus == 0 \
                and not Ignore(player,otherplayer,ignoredict):
                    adjacentmakeupminutes += minutesdict[otherplayer]
                if otherstatus == 1 \
                and not Ignore(player,otherplayer,ignoredict):
                    adjacentmakeupminutes += minutesdict[otherplayer]/2
                    print(player,"adjacent injury",otherplayer,\
                          minutesdict[otherplayer])
    
    
    return [expectedminutes,[playerspot,rotationbin,makeupminutes,\
    adjacentmakeupminutes]]