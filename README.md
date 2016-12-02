# dfs
Daily Fantasy Basketball Prediction

Collection of programs to make expected daily fantasy points predictions for Excel spreadsheet of players using machine learning algorithm.
Files include:

FD.py: main function.  
Requires input: Excel spreadsheet, feature and response variables for machine learning algorithm.  
Output: Excel spreadsheet with predictions, updates dataframes of feature and response variables.

DataCollection.py: Responsible for web scraping to collect data for all players.

MachineLearning.py: Functions responsible for modifying and performing analysis on pandas dataframes holding feature and response variables.

MyFunctions.py: Other assorted functions called by main.  

Dicts.py: Collection of dictionaries necessary throughout other programs in package.
