# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 13:04:34 2016

@author: evansmothers
"""

from bs4 import BeautifulSoup
import urllib
import math
import numpy
import pandas as pd
import MyFunctions
import Dicts
import datetime


##################################GETPACE###################################

def GetPace():
    ''' Get pace data '''
    url4 = "http://www.espn.com/nba/hollinger/teamstats"
    page4 = urllib.request.urlopen(url4)
    soup4 = BeautifulSoup(page4.read(),"lxml")
    table4 = soup4.find("table", attrs = {"class": "tablehead"})
    column_headers4 = [td.getText() for td in \
    table4.findAll("tr",limit=2)[1].findAll("td")]
    data_rows4 = table4.findAll("tr")[2:]
    teamdata = [[td.getText().replace('*','') for td in data_rows4[i].findAll("td")]\
    for i in range(len(data_rows4))]
    df4 = pd.DataFrame(teamdata,columns = column_headers4)
    
    return df4
    
##############################GETDEFENSIVESPLITS############################
    
def GetDefensiveSplits():
  
#    ''' Get position-specific defensive data and save in a list of data frames '''
#    defsplits = []
#    baseurl = "http://www.rotowire.com/daily/nba/defense-vspos.htm"
#    for position in Dicts.positions:
#        url5 = baseurl
#        if position != "PG":
#            url5 += "?pos=" + position
#        page5 = urllib.request.urlopen(url5)
#        soup5 = BeautifulSoup(page5.read(),"lxml")
#        table5 = soup5.find("table")
#        column_headers5 = [th.getText() for th in \
#        table5.findAll("tr",limit=2)[1].findAll("th")]
#        data_rows5 = table5.findAll("tr")[1:]
#        teamdata2 = [[td.getText() for td in data_rows5[i].findAll("td")] \
#        for i in range(len(data_rows5))]
#        df5 = pd.DataFrame(teamdata2,columns = column_headers5)
#        
#        '''Remove empty rows (DNP), convert elements to float '''
#        df5 = df5[df5.Season.notnull()]
#        df5.Season = [float(element) for element in df5.Season]
#        defsplits.append(df5)

    ''' Get position-specific defensive data and save in a list of data frames '''
    defsplitslist = []
    position_list = []
    url = "http://www.sportingcharts.com/nba/defense-vs-position/"
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(),"lxml")
    tables = soup.findAll("table", attrs = \
    {"class": "table table-condensed table-responsive table-hover"})
    for i in range(0,len(tables)):
        table = tables[i]
        table_position = [th.getText() for th in table.findAll("tr")[0].findAll("th")][0]
        column_headers = [th.getText() for th in table.findAll("tr")[1].findAll("th")]
        data_rows = [[td.getText() for td in tr.findAll("td")] for tr in table.findAll("tr")[2:]]
        df = pd.DataFrame(data_rows, columns = column_headers)
        df["Team"] = df["Team"].map(lambda x: x.upper())
        position_list.append(\
                Dicts.positionslist[table_position.replace("\n","").lstrip()])
        defsplitslist.append(df)
    
    defsplitsdict = {position_list[i]: defsplitslist[i] \
                 for i in range(0,len(position_list)) }
    defsplits = [defsplitsdict[Dicts.positions[i]] \
                 for i in range(0,len(Dicts.positions))]
    defsplits = [df.apply(lambda x: pd.to_numeric(x, errors='ignore')) \
                 for df in defsplits]
    
        

    return defsplits
 
#################################GETFILENAMES###############################
        
def GetFileNames():
    ''' Create datetime strings for naming files '''
    now = datetime.datetime.now()
    nowday = str(now.day)
    if len(nowday) == 1:
        nowday = '0' + nowday
    nowmonth = str(now.month)
    if len(nowmonth) == 1:
        nowmonth = '0' + nowmonth
    nowyear = str(now.year)[2:]
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterdayday = str(yesterday.day)
    if len(yesterdayday) == 1:
        yesterdayday = '0' + yesterdayday
    yesterdaymonth = str(yesterday.month)
    if len(yesterdaymonth) == 1:
        yesterdaymonth = '0' + yesterdaymonth
    yesterdayyear = str(yesterday.year)[2:]
    todayfilename = nowmonth+nowday+nowyear
    yesterdayfilename = yesterdaymonth+yesterdayday+yesterdayyear  
    
    return [todayfilename,yesterdayfilename]

##################################GOTOVEGAS#################################
    
def GoToVegas(todayscsv):
    ''' Get list of eligible games for the day '''
    todaysgames = list(todayscsv.Game.unique())
    
    ''' Non-abbreviated teamsforlines '''
    teamsforlines = [[Dicts.abbreviations[game[:game.find("@")]], \
    Dicts.abbreviations[game[game.find("@")+1:]]] for game in todaysgames]
    
    ''' Abbreviated teamsforlines '''
    teamsforlines = \
    [[game[:game.find("@")],game[game.find("@")+1:]] for game in todaysgames]
    teamsforlines = [[Dicts.vegasexceptions[team] if team \
    in Dicts.vegasexceptions else team for team in matchup] \
    for matchup in teamsforlines]
                    
    ''' Get average magnitude of Vegas line, over/under for all NBA teams '''
    avglinedict = {}
    avgoverunderdict = {}
    baseurl10 = "https://www.teamrankings.com/nba/team/"
    for key in Dicts.teams:
        url10 = baseurl10 + Dicts.teams[key].replace(" ","-").lower() + "/"
        page10 = urllib.request.urlopen(url10)
        soup10 = BeautifulSoup(page10.read(),"lxml")
        table10 = soup10.find("table", attrs = {"class": \
        "tr-table datatable scrollable"})
        column_headers10 = [th.getText() for th in \
        table10.find("tr").findAll("th")]
        data_rows10 =  table10.findAll("tr")[1:]
        teamdata3 = [[td.getText() for td in data_rows10[i].findAll("td")] \
        for i in range(len(data_rows10))]

        
        ''' Remove rows with games that haven't happened yet '''   
        teamdata3 = [teamdata3[i] for i in range(len(teamdata3)) if \
        teamdata3[i][4] != '']
        
        ''' Get list of Vegas lines for all games '''    
        expectedMOV = [abs(float(teamdata3[i][6]))\
        for i in range(len(teamdata3))]
        
        ''' Get list of over/under for all games '''
        overundercol = [teamdata3[i][7] for i in range(len(teamdata3))]
        
        ''' Clean up list of over/under for all games '''
        overundercol = [term.replace('Ov ','') for term in overundercol]
        overundercol = [term.replace('Pu ','') for term in overundercol]
        overundercol = [float(term.replace('Un ','')) for term in overundercol]
        
        ''' Get line and over/under averages '''
        avglinedict[Dicts.teams[key]] = numpy.mean(expectedMOV)
        avgoverunderdict[Dicts.teams[key]] = numpy.mean(overundercol)


        
#        
#    ALTERNATIVE VERSION OF THIS SECTION FORTHCOMING
        
    ''' Obtain Vegas lines and over/under'''
    url7 = "http://m.espn.go.com/nba/dailyline"
    page7 = urllib.request.urlopen(url7)
    soup7 = BeautifulSoup(page7.read(),"lxml")
    table7 = soup7.find("table")
    data_rows7 = [tr for tr in table7.findAll("tr")[1:]]
    teamsandlines = [[td.getText() for td in data_rows7[i].findAll("td")] \
    for i in range(len(data_rows7))]
    ''' Replace even lines with 0's '''
    for game in teamsandlines:
        if game[1] == '--':
            game[1] = '0'
#
#
#    ''' Obtain Vegas lines and over/under'''
#    myurl = "https://www.vegas.com/gaming/sportsline/basketball/"
#    mypage = urllib.request.urlopen(myurl)
#    mysoup = BeautifulSoup(mypage.read(),"lxml")
#    mytable = mysoup.find("table", attrs = {"class": "sportsline"})
#    my_column_headers = \
#    [td.getText() for td in mytable.findAll("tr")[1].findAll("td")]
#    my_data_rows = [[td.getText() for td in element.findAll("td")] for \
#                    element in mytable.findAll("tr")[2:]]
#    index_col = [row[my_column_headers.index("Time")] \
#                       for row in my_data_rows if len(row) > 1]
#    data_col =  [row[my_column_headers.index("Time")+1] \
#                       for row in my_data_rows if len(row) > 1]  
#    favorite_indices = [i for i, x in enumerate(index_col) if x == "Favorite"]
#    line_indices = [i for i, x in enumerate(index_col) if x == "Point spread"]
#    over_under_indices = [i for i, x in enumerate(index_col) if x == "Total"]
#    favorite_dict = {data_col[favorite_indices[i]]: \
#    [abs(float(data_col[line_indices[i]].replace('½','.5'))), \
#    float(data_col[over_under_indices[i]].replace('o/u','').replace('½','.5'))] \
#    for i in range(0,len(favorite_indices))}
#    favorite_dict.update(GetUnderdog(teamsforlines,favorite_dict))
#    teamsandlines = favorite_dict.copy()
#    teamsandlines = {Dicts.teams[Dicts.abbreviations[key]]: \
#                      teamsandlines[key] for key in teamsandlines}
#    linedict = {team: teamsandlines[team][0] for team in teamsandlines}
#    overunderdict = {team: teamsandlines[team][1] for team in teamsandlines}

    
    ''' Clean up NANs in avglinedict, avgoverunderdict '''
    avglinedict = {key: 0.0 if math.isnan(avglinedict[key]) else avglinedict[key] \
                   for key in avglinedict}
    avgoverunderdict = {key: 200.0 if math.isnan(avgoverunderdict[key]) else avgoverunderdict[key] \
                   for key in avglinedict}
    
    ''' Dictionaries for favored teams '''    
    favteamlinedict = {Dicts.abbreviations[element[0].upper()]: \
    abs(float(element[1])) for element in teamsandlines}
    favteamoverunderdict = {Dicts.abbreviations[element[0].upper()]: \
    float(element[3]) for element in teamsandlines}
    
    ''' Dictionaries for underdog teams '''
    underteamlinedict = {Dicts.abbreviations[element[2].upper()]: \
    -1*abs(float(element[1])) for element in teamsandlines}
    underteamoverunderdict = {Dicts.abbreviations[element[2].upper()]: \
    float(element[3]) for element in teamsandlines}
    
    ''' Merge each into a single dictionary for all teams '''
    linedict = favteamlinedict.copy()    
    linedict.update(underteamlinedict)
    overunderdict = favteamoverunderdict.copy()
    overunderdict.update(underteamoverunderdict)
    
    ''' Convert to long team names '''
    linedict = {Dicts.teams[team]: linedict[team] for team in linedict}
    overunderdict = {Dicts.teams[team]: overunderdict[team] \
                     for team in overunderdict}            

    ''' MOCK AVGLINEDICT AND AVGOVERUNDERDICT '''
    avglinedict = {Dicts.teams[team]: 0.0 for team in Dicts.teams}
    avgoverunderdict = {Dicts.teams[team]: 200.0 for team in Dicts.teams}
    
    ''' Create adjusted line dict and adjusted over/under dict '''
    adjustedlinedict = {key: linedict[key] - \
                        avglinedict[key] for key in linedict}
    adjustedoverunderdict = {key: overunderdict[key] - \
                        avgoverunderdict[key] for key in overunderdict}
    
    return [adjustedlinedict,adjustedoverunderdict]

################################GETUNDERDOG#################################

def GetUnderdog(teamsforlines,favorite_dict):
    ''' Get line and over/under for underdog teams given favorites dict '''
    underdogdict = {}
    for matchup in teamsforlines:
        teama = matchup[0]
        teamb = matchup[1]
        if teama in favorite_dict:
            underdog = teamb
            favorite = teama
        elif teamb in favorite_dict:
            underdog = teama
            favorite = teamb
        else:
            print("You fucked up")
        underdogdict[underdog] = favorite_dict[favorite]
    
    return underdogdict
                                   
        
###############################GETDEPTHCHARTS###############################

def GetDepthCharts():
    ''' Get depth charts for all teams '''
    teamlist = [key for key in Dicts.abbreviations \
    if key != 'PHX' and key != 'UTAH' and key != 'SAS' and key != 'GSW' \
    and key != 'NYK']
    teamlist.sort()
    bknindex = teamlist.index('BKN')
    bosindex = teamlist.index('BOS')
    saindex = teamlist.index('SA')
    sacindex = teamlist.index('SAC')
    teamlist[bknindex] = 'BOS'
    teamlist[bosindex] = 'BKN'
    teamlist[saindex] = 'SAC'
    teamlist[sacindex] = 'SA'
    
    dcurl = 'http://basketball.realgm.com/nba/visual-depth-charts'
    dcpage = urllib.request.urlopen(dcurl)
    dcsoup = BeautifulSoup(dcpage.read(),"lxml")
    dcteams = [team for team in dcsoup.findAll("table")]
    depthcharts = {}
    i = 0
    for currentteam in dcteams:
        teampositions = ["Role"] + [th.getText() for th in \
        currentteam.find("tr").findAll("th")[1:]]
        currentteamtable = [[MyFunctions.Clean(td.getText()) for td in tr.findAll("td")] \
        for tr in currentteam.findAll("tr")[1:]] 
        rolelist = []
        pglist = []
        sglist = []
        sflist = []
        pflist = []
        clist = []
        for row in currentteamtable:
            rolelist.append(row[0])
            pglist.append(row[1])
            sglist.append(row[2])
            sflist.append(row[3])
            pflist.append(row[4])
            clist.append(row[5])
        fulllist = [rolelist,pglist,sglist,sflist,pflist,clist]
        teamdepthchart = {teampositions[i]: fulllist[i] \
        for i in range(len(teampositions))}
        depthcharts[teamlist[i]] = teamdepthchart
        i += 1
        
    return depthcharts

    
################################GETMINUTESDICT###############################   

def GetMinutesDict(todayscsv):
    ''' POSSIBLE ALTERNATIVE SITE:
        https://basketballmonster.com/PlayerRankings.aspx '''
    ''' Last 5 games minutes average for injuries: creating data frame '''
    ivec = ['2','3','4','5','6']
    ignoremelist = ['Aaron Harrison']   
    minutesdf2 = pd.DataFrame([],[])
    for pos in ivec:
        minutesurl2 = "http://www.hoopsstats.com/basketball/fantasy/nba/playerstats/17/" + pos + "/eff/5-1"
        minutespage2 = urllib.request.urlopen(minutesurl2)
        minutessoup2 = BeautifulSoup(minutespage2.read(),"lxml")
        minutestable2 = minutessoup2.find("table", attrs = {"width": "99%"})
        minutesheadersrow2 = minutestable2.find("table", attrs = \
        {"class": "tableheadline", "width": "100%", "height": "23"})
        minutescolumnheaders2 = [td.getText() \
        for td in minutesheadersrow2.findAll("td")] + ['Pos'] 
        minutesdata_rows2 = [[td.getText() for td in table.findAll("td")] + \
        [int(pos)-1] for table in minutestable2.findAll("table")[6:]]
        posdf2 = pd.DataFrame(minutesdata_rows2,columns=minutescolumnheaders2)    
        minutesdf2 = minutesdf2.append(posdf2,ignore_index = True)
    
    ''' Match data frame to player list, create minutes dictionary '''
    namesabbrev = {todayscsv["First Name"][i] + " " + \
    todayscsv["Last Name"][i]: [todayscsv["First Name"][i][0] + ". " + \
    todayscsv["Last Name"][i],Dicts.posnum[todayscsv["Position"][i]]] \
    for i in range(len(todayscsv["First Name"]))}
    namesabbrev = {key: Check(key,namesabbrev[key]) for key in namesabbrev}
    minutesdict = {}
    for key in namesabbrev:
        print(key,namesabbrev[key])
        if key in Dicts.abbrevexceptions.keys():
            if len(Dicts.abbrevexceptions[key]) == 2:
                minutesdict[key] = float(minutesdf2[minutesdf2["Player"] \
                == Dicts.abbrevexceptions[key][0]][minutesdf2["Pos"] == \
                Dicts.abbrevexceptions[key][1]]["Min"])*\
                float(minutesdf2[minutesdf2["Player"] == \
                Dicts.abbrevexceptions[key][0]][minutesdf2["Pos"] == \
                Dicts.abbrevexceptions[key][1]]["G"])/5
            elif len(Dicts.abbrevexceptions[key]) == 1:
                copyurl = Dicts.abbrevexceptions[key][0]
                copypage = urllib.request.urlopen(copyurl)
                copysoup = BeautifulSoup(copypage.read(),"lxml")
                copytable = copysoup.find("div", attrs = \
                {"class": "mod-container mod-table mod-player-stats"})
                copycolumn_headers = [td.getText() for td in \
                copytable.find("tr", attrs = {"class": "colhead"})]
                copydata_rows = [[td.getText() for td in tr] \
                for tr in copytable.findAll("tr")[2:]]
                copydf = pd.DataFrame(copydata_rows,columns=copycolumn_headers)
                copydf = copydf[copydf.PTS.notnull()]
                copydf = copydf[copydf.PTS != "PTS"]
                minutesdict[key] = \
                numpy.mean(copydf.head(5).MIN.astype("float"))
            else:
                minutesdict[key] = 0.0
        
        elif namesabbrev[key][0] in minutesdf2.Player.values \
        and key not in ignoremelist:
            minutesdict[key] = \
            float(minutesdf2[minutesdf2["Player"] == namesabbrev[key][0]]["Min"]) \
            *float(minutesdf2[minutesdf2["Player"] == namesabbrev[key][0]]["G"]) \
            /5
        else:
            minutesdict[key] = 0.0

    return minutesdict
    
###################################CHECK#####################################

''' Check if name needs to be adjusted using Dicts list '''
def Check(key,abbrevandpos):
    if key in Dicts.namechanges.keys():
        return [Dicts.namechanges[key],abbrevandpos[1]]
    return abbrevandpos
  