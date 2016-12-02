# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 12:11:14 2016

@author: evansmothers
"""

''' List of teams and player positions '''
teams = {"Atlanta": "Atlanta Hawks", "Boston": "Boston Celtics",\
"Brooklyn": "Brooklyn Nets", "Charlotte": "Charlotte Hornets",\
"Chicago": "Chicago Bulls", "Cleveland": "Cleveland Cavaliers", \
"Dallas": "Dallas Mavericks", "Denver": "Denver Nuggets", \
"Detroit": "Detroit Pistons", "Golden State": "Golden State Warriors", \
"Houston": "Houston Rockets", "Indiana": "Indiana Pacers", \
"LA Clippers": "Los Angeles Clippers", "LA Lakers": "Los Angeles Lakers", \
"Memphis": "Memphis Grizzlies", "Miami": "Miami Heat", \
"Milwaukee": "Milwaukee Bucks", "Minnesota": "Minnesota Timberwolves", \
"New Orleans": "New Orleans Pelicans", "New York": "New York Knicks", \
"Oklahoma City": "Oklahoma City Thunder", "Orlando": "Orlando Magic", \
"Philadelphia": "Philadelphia 76ers", "Phoenix": "Phoenix Suns", \
"Portland": "Portland Trail Blazers", "Sacramento": "Sacramento Kings", \
"San Antonio": "San Antonio Spurs", "Toronto": "Toronto Raptors", \
"Utah": "Utah Jazz", "Washington": "Washington Wizards"}
abbreviations = {"ATL": "Atlanta", "BKN": "Brooklyn", "BOS": "Boston", \
"CHA": "Charlotte", "CHI": "Chicago", "CLE": "Cleveland", "DAL": "Dallas", \
"DEN": "Denver", "DET": "Detroit", "GS": "Golden State", "GSW": "Golden State", \
"HOU": "Houston", "IND": "Indiana", "LAC": "LA Clippers", "LAL": "LA Lakers", \
"MEM": "Memphis", "MIA": "Miami", "MIL": "Milwaukee", "MIN": "Minnesota", \
"NO": "New Orleans", "NY": "New York", "NYK": "New York", \
"OKC": "Oklahoma City", "ORL": "Orlando", "PHI": "Philadelphia", \
"PHO": "Phoenix", "PHX": "Phoenix", "POR": "Portland", "SAC": "Sacramento", \
"SA": "San Antonio", "SAS": "San Antonio", "TOR": "Toronto", "UTA": "Utah", \
"UTAH": "Utah", "WAS": "Washington", "WSH": "Washington"}
positions = ["PG","SG","SF","PF","C"]
positionslist = {"Point Guard": "PG", "Shooting Guard": "SG", \
"Small Forward": "SF", "Power Forward": "PF", "Center": "C", \
"Point Guards": "PG", "Shooting Guards": "SG", \
"Small Forwards": "SF", "Power Forwards": "PF", "Centers": "C"}
posnum = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
''' List of exceptions to URL rules '''
exceptions = {"Jeff Ayres": "http://www.basketball-reference.com/players/p/pendeje02", \
"Harrison Barnes": "http://www.basketball-reference.com/players/b/barneha02", \
"Matt Barnes": "http://www.basketball-reference.com/players/b/barnema02", \
"Keith Benson": "http://www.basketball-reference.com/players/b/bensoke02", \
"Bojan Bogdanovic": "http://www.basketball-reference.com/players/b/bogdabo02", \
"Ronnie Brewer": "http://www.basketball-reference.com/players/b/brewero02", \
"Anthony Brown": "http://www.basketball-reference.com/players/b/brownan02", \
"Bobby Brown": "http://www.basketball-reference.com/players/b/brownbo02", \
"Jaylen Brown": "http://www.basketball-reference.com/players/b/brownja02", \
"Markel Brown": "http://www.basketball-reference.com/players/b/brownma02", \
"Clint Capela": "http://www.basketball-reference.com/players/c/capelca01", \
"Daequan Cook": "http://www.basketball-reference.com/players/c/cookda02", \
"Jordan Crawford": "http://www.basketball-reference.com/players/c/crawfjo02", \
"Anthony Davis": "http://www.basketball-reference.com/players/d/davisan02", \
"Larry Drew": "http://www.basketball-reference.com/players/d/drewla02", \
"Mike Dunleavy": "http://www.basketball-reference.com/players/d/dunlemi02", \
"Diante Garrett": "http://www.basketball-reference.com/players/g/garredi02", \
"Jerian Grant": "http://www.basketball-reference.com/players/g/grantje02", \
"Danny Green": "http://www.basketball-reference.com/players/g/greenda02", \
"Jeff Green": "http://www.basketball-reference.com/players/g/greenje02", \
"P.J. Hairston": "http://www.basketball-reference.com/players/h/hairspj02", \
"Jordan Hamilton": "http://www.basketball-reference.com/players/h/hamiljo02", \
"Tim Hardaway Jr.": "http://www.basketball-reference.com/players/h/hardati02", \
"Tobias Harris": "http://www.basketball-reference.com/players/h/harrito02", \
"Gerald Henderson": "http://www.basketball-reference.com/players/h/hendege02", \
"Guillermo Hernangomez": "http://www.basketball-reference.com/players/h/hernawi01", \
"Willy Hernangomez": "http://www.basketball-reference.com/players/h/hernawi01", \
"Chris Johnson": "http://www.basketball-reference.com/players/j/johnsch04", \
"Joe Johnson": "http://www.basketball-reference.com/players/j/johnsjo02", \
"Stanley Johnson": "http://www.basketball-reference.com/players/j/johnsst04", \
"Darius Johnson-Odom": "http://www.basketball-reference.com/players/j/johnsda03", \
"Dahntay Jones": "http://www.basketball-reference.com/players/j/jonesda02", \
"James Jones": "http://www.basketball-reference.com/players/j/jonesja02", \
"Brandon Knight": "http://www.basketball-reference.com/players/k/knighbr03", \
"David Lee": "http://www.basketball-reference.com/players/l/leeda02", \
"John Lucas": "http://www.basketball-reference.com/players/l/lucasjo02", \
"John Lucas III": "http://www.basketball-reference.com/players/l/lucasjo02", \
"Kevin Martin": "http://www.basketball-reference.com/players/m/martike02", \
"Wesley Matthews": "http://www.basketball-reference.com/players/m/matthwe02", \
"Andre Miller": "http://www.basketball-reference.com/players/m/millean02", \
"Patrick Mills": "http://www.basketball-reference.com/players/m/millspa02", \
"Patty Mills": "http://www.basketball-reference.com/players/m/millspa02", \
"Marcus Morris": "http://www.basketball-reference.com/players/m/morrima03", \
"Markieff Morris": "http://www.basketball-reference.com/players/m/morrima02", \
"Xavier Munford": "http://www.basketball-reference.com/players/m/munfoxa02", \
"Larry Nance Jr.": "http://www.basketball-reference.com/players/n/nancela02", \
"Sasha Pavlovic": "http://www.basketball-reference.com/players/p/pavloal01", \
"Willie Reed": "http://www.basketball-reference.com/players/r/reedwi02", \
"Glen Rice Jr.": "http://www.basketball-reference.com/players/r/ricegl02", \
"Andre Roberson": "http://www.basketball-reference.com/players/r/roberan03", \
"Glenn Robinson III": "http://www.basketball-reference.com/players/r/robingl02", \
"Jakarr Sampson": "http://www.basketball-reference.com/players/s/sampsja02", \
"Jonathon Simmons": "http://www.basketball-reference.com/players/s/simmojo02", \
"Chris Smith": "http://www.basketball-reference.com/players/s/smithch05", \
"Greg Smith": "http://www.basketball-reference.com/players/s/smithgr02", \
"Jason Smith": "http://www.basketball-reference.com/players/s/smithja02", \
"Josh Smith": "http://www.basketball-reference.com/players/s/smithjo03", \
"Jeffery Taylor": "http://www.basketball-reference.com/players/t/tayloje03", \
"Jermaine Taylor": "http://www.basketball-reference.com/players/t/tayloje02", \
"Isaiah Thomas": "http://www.basketball-reference.com/players/t/thomais02", \
"Jason Thompson": "http://www.basketball-reference.com/players/t/thompja02", \
"Henry Walker": "http://www.basketball-reference.com/players/w/walkebi01", \
"Kemba Walker": "http://www.basketball-reference.com/players/w/walkeke02", \
"Martell Webster": "http://www.basketball-reference.com/players/w/webstma02", \
"Royce White": "http://www.basketball-reference.com/players/w/whitero03", \
"Damien Wilkins": "http://www.basketball-reference.com/players/w/wilkida02", \
"Alan Williams": "http://www.basketball-reference.com/players/w/willial03", \
"Derrick Williams": "http://www.basketball-reference.com/players/w/willide02", \
"Lou Williams": "http://www.basketball-reference.com/players/w/willilo02", \
"Marcus Williams": "http://www.basketball-reference.com/players/w/willima04", \
"Marvin Williams": "http://www.basketball-reference.com/players/w/willima02", \
"Mo Williams": "http://www.basketball-reference.com/players/w/willima01", \
"Reggie Williams": "http://www.basketball-reference.com/players/w/willire02", \
"Shawne Williams": "http://www.basketball-reference.com/players/w/willish03", \
"Troy Williams": "http://www.basketball-reference.com/players/w/willitr02", \
"Metta World Peace": "http://www.basketball-reference.com/players/a/artesro01", \
"Brandan Wright": "http://www.basketball-reference.com/players/w/wrighbr03", \
"Roy Devyn Marble": "http://www.basketball-reference.com/players/m/marblro02", \
"J.J. Barea": "http://www.basketball-reference.com/players/b/bareajo01", \
"Taurean Prince": "http://www.basketball-reference.com/players/p/princta02" \
}
depthchartexceptions = {"Brad Beal": "Bradley Beal", "Ishmael Smith": \
"Ish Smith", "Jakarr Sampson": "JaKarr Sampson", "Kelly Oubre": "Kelly Oubre, Jr.", "Matthew Dellavedova": \
"Matt Dellavedova", "Larry Nance Jr.": "Larry Nance, Jr.", "Jose Juan Barea": \
"J.J. Barea", "Luc Richard Mbah a Moute": "Luc Mbah a Moute", \
"Marcelo Huertas": "Marcelinho Huertas", "Roy Devyn Marble": "Devyn Marble", \
"RJ Hunter": "R.J. Hunter", "Louis Amundson": "Lou Amundson", "Raul Neto": \
"Raulzinho Neto", "Bryce Jones": "Bryce Dejean-Jones", "Joseph Young": \
"Joe Young", "Glenn Robinson III": "Glenn Robinson", "Patrick Mills": \
"Patty Mills", "Walter Tavares": "Edy Tavares", "Louis Williams": \
"Lou Williams", "Domantas Sabonis": "Domas Sabonis", \
"Guillermo Hernangomez": "Willy Hernangomez"}
depthchartadjust = {"Manu Ginobili": 1, "Jamal Crawford": 1, \
"Robert Covington": 1, "Hollis Thompson": 2, "Jerami Grant": 3, \
"Markieff Morris": 1}
namechanges = {"Luc Richard Mbah a Moute": "L. Mbah A Moute", \
"Roy Devyn Marble": "D. Marble", "Bryce Jones": "B. Dejean-Jones", \
"Glenn Robinson III": "G. Robinson III", "Larry Nance Jr.": "L. Nance Jr.", \
"Stephen Zimmerman Jr.": "S. Zimmerman", "Otto Porter": "O. Porter Jr.", \
"Guillermo Hernangomez": "W. Hernangomez"}
abbrevexceptions = {'Stephen Curry': ['S. Curry', 1], \
'Justin Holiday': ['J. Holiday', 2], 'Seth Curry': ['S. Curry', 2], \
'Jerian Grant': ['J. Grant', 1], 'Mo Williams': ['M. Williams', 1], \
'J.R. Smith': ['J. Smith', 2], 'Jason Smith': ['J. Smith', 5], \
'Marcus Morris': ['M. Morris', 3], \
'Jeff Green': ['J. Green', 3], 'Justin Anderson': ['J. Anderson', 2], \
'Draymond Green': ['D. Green', 4], 'Marvin Williams': ['M. Williams', 4], \
 'Markieff Morris': ['M. Morris', 4], 'Josh Smith': ['J. Smith', 4], \
'Jerami Grant': ['J. Grant', 4], 'Deron Williams': ['D. Williams', 1], \
'JaMychal Green': ['J. Green', 4], 'Danny Green': ['D. Green', 2], \
'Terrence Jones': ['T. Jones', 4], 'Tyus Jones': ['T. Jones', 1], \
'P.J. Hairston': ['P. Hairston', 3], \
'Lance Stephenson': ['L. Stephenson', 2], \
'Andrew Harrison': ['A. Harrison', 1], 'Derrick Williams': ['D. Williams', 4],  \
'Michael Beasley': ['M. Beasley', 4], 'Malik Beasley': ['M. Beasley', 2], \
'James Young': ['http://espn.go.com/nba/player/gamelog/_/id/3064509/james-young'], \
'Joseph Young': ['http://espn.go.com/nba/player/gamelog/_/id/2528386/joe-young'], \
'Joe Young': ['http://espn.go.com/nba/player/gamelog/_/id/2528386/joe-young'],
'James Johnson':['http://espn.go.com/nba/player/gamelog/_/id/3999/james-johnson'], \
'Joe Johnson': ['http://espn.go.com/nba/player/gamelog/_/id/1007/joe-johnson'], \
'Mason Plumlee': ['http://espn.go.com/nba/player/gamelog/_/id/2488653/mason-plumlee'], \
'Miles Plumlee': ['http://espn.go.com/nba/player/gamelog/_/id/6616/miles-plumlee'], \
'Marshall Plumlee': ['http://www.espn.com/nba/player/gamelog/_/id/2566748/marshall-plumlee'], \
'Jrue Holiday': ['http://www.espn.com/nba/player/gamelog/_/id/3995/jrue-holiday']}
depthchartignore = ["Elijah Millsap", "Lorenzo Brown", "Cory Jefferson", \
"Bryce Jones", "Bryce Dejean-Jones", "Ryan Hollins", "Phil (Flip) Pressey", \
"Christian Wood"]
vegasexceptions = {"NY": "NYK", "SA": "SAS", "GS": "GSW"}



''' 'James Anderson': ['J. Anderson', 2],  '''
''' 'Jrue Holiday': ['J. Holiday', 1],  '''
''' 'Aaron Harrison': ['A. Harrison', 2], '''
''' 'Randy Foye': ['R. Foye', 2],  '''
'''  '''