# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 09:46:32 2016

@author: evansmothers
"""
from bs4 import BeautifulSoup
import urllib
import MyFunctions
import numpy as np
import math
import pickle
import pandas as pd
import csv
from sklearn import linear_model
from sklearn import neighbors
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import KFold

#############################EXPORTFEATUREVARIABLES###########################

def ExportFeatureVariables(fppmdfX,mindfX,todayfilename):
    
    ''' Export day's feature variables to FPPM and min files '''
    with open("Database/" + todayfilename + "fppm.p", "wb") as handle:
        pickle.dump(fppmdfX,handle)
    with open("Database/" + todayfilename + "min.p", "wb") as handle:
        pickle.dump(mindfX,handle)

#############################GETYESTERDAYSALARYDICT##########################

def GetYesterdaySalaryDict(salarydict,todayfilename,yesterdayfilename,\
                           yesterdayboolnew):
    
    ''' Export today's salary dict to file '''
    with open("Database/" + todayfilename + "salarydict.p", "wb") as handle:
        pickle.dump(salarydict,handle)
    
    if yesterdayboolnew:    
        ''' Load yesterday's salary dict if it exists'''
        with open("Database/" + yesterdayfilename + "salarydict.p", "rb") as handle:
            yesterdaysalarydict = pickle.load(handle)
    else:
        yesterdaysalarydict = {}
        
    return yesterdaysalarydict
    
################################GETYESTERDAYSDF#################################
''' Return yesterday's full dataframe if program ran yesterday '''
def GetYesterdaysDF(yesterdayfilename,yesterdaybool,yesterdayboolnew,\
                    yesterdaysalarydict):
    if yesterdaybool:        
        ''' Import feature variables as saved from yesterday in df '''
        with open("Database/" + yesterdayfilename + "fppm.p", "rb") as handle:
            yesterdayfppmX = pickle.load(handle) 
        with open("Database/" + yesterdayfilename + "min.p", "rb") as handle:
            yesterdayminX = pickle.load(handle)        
        
        ''' Get yesterday's actuals, create df of response variables '''
        yesterdayactual = Yesterday()
        yesterdayfppmY = yesterdayactual.FPPM
        yesterdayminY = yesterdayactual.Min
        
        ''' Create full dataframe with yesterday's feature and response variables '''
        yesterdayfppmfull = pd.concat([yesterdayfppmX,yesterdayfppmY],axis=1,\
        join='inner')
        yesterdayminfull = pd.concat([yesterdayminX,yesterdayminY],axis=1,\
        join='inner')
        
        ''' Clean up yesterday's dataframes to eliminate outliers '''
        yesterdayfppmfull = yesterdayfppmfull[yesterdayfppmfull.FPPM != 0]
        yesterdayminfull = yesterdayminfull[yesterdayminfull.Min > 0]
            
    
    else:    
        yesterdayfppmfull = pd.DataFrame([])
        yesterdayminfull = pd.DataFrame([])
        
    if yesterdayboolnew:
        ''' Call function to form full FP dataframe of yesterday's stats '''
        yesterdayfpdf = FormFullFPDF(yesterdayfppmfull,yesterdayminfull,\
                                     yesterdaysalarydict)    
    else:
        yesterdayfpdf = pd.DataFrame([])
 
    
    return[yesterdayfppmfull,yesterdayminfull,yesterdayfpdf]

#################################FORMFULLFPDF################################

def FormFullFPDF(yesterdayfppmfull,yesterdayminfull,yesterdaysalarydict):
    fulldf = pd.concat([yesterdayfppmfull,yesterdayminfull], axis=1)
    fulldf['FP'] = fulldf['FPPM'] * fulldf['Min']

    ''' Add salary column to dataframe '''
    for element in fulldf.index.values:
        if element in yesterdaysalarydict.keys():
            fulldf.loc[element,'Salary'] = int(yesterdaysalarydict[element])
    
    ''' Delete rows with zero salary '''
    fulldf = fulldf[fulldf.Salary != 0]
    fulldf = fulldf[np.isfinite(fulldf['FP'])]

    ''' Add column for FP/Salary '''
    fulldf['FPValue'] = fulldf['FP'] / fulldf['Salary'] * ([1000] * len(fulldf))
    
    return(fulldf)

###################################GETFULLDF###################################
    
def GetFullDF(yesterdayfppmfull,yesterdayminfull,yesterdayfpfull,\
              dfbool,firstofdaybool,dfboolnew):
    if dfbool and firstofdaybool:
        ''' Open previous full dataframe '''
        with open("Machine Learning/fppmdffull.p","rb") as handle:
            fppmdfold = pickle.load(handle)
        with open("Machine Learning/mindffull.p","rb") as handle:
            mindfold = pickle.load(handle)
            
        ''' Safeguard: save yesterday's full dataframes to different file '''
        with open("Machine Learning/fppmdfprevious.p","wb") as handle:
            pickle.dump(fppmdfold,handle)
        with open("Machine Learning/mindfprevious.p","wb") as handle:
            pickle.dump(mindfold,handle) 
            
        ''' Merge full dataframe with yesterday's data '''
        fppmdffull = pd.concat([yesterdayfppmfull,fppmdfold],axis=0,\
        ignore_index=True)
        mindffull = pd.concat([yesterdayminfull,mindfold],axis=0,\
        ignore_index=True)
            
    elif firstofdaybool:
        fppmdffull = yesterdayfppmfull.reset_index(drop=True)
        mindffull = yesterdayminfull.reset_index(drop=True)
        
    else:
        with open("Machine Learning/fppmdffull.p","rb") as handle:
            fppmdffull = pickle.load(handle)
        with open("Machine Learning/mindffull.p", "rb") as handle:
            mindffull = pickle.load(handle)
    
##     NEW STUFF HERE
            
    if dfboolnew and firstofdaybool:
        ''' Open previous full dataframe '''
        with open("Machine Learning/fpdffull.p","rb") as handle:
            fpdfold = pickle.load(handle)
            
        ''' Safeguard: save yesterday's full dataframe '''
        with open("Machine Learning/fpdfprevious.p","wb") as handle:
            pickle.dump(fpdfold,handle)
        
        ''' Merge full dataframe with yesterday's data '''
        fpdffull = pd.concat([yesterdayfpfull,fpdfold],axis=0,\
        ignore_index=True)
    
    elif firstofdaybool:
        fpdffull = yesterdayfpfull.reset_index(drop=True)
    
    else:
        with open("Machine Learning/fpdffull.p", "rb") as handle:
            fpdffull = pickle.load(handle)
        
    ''' Delete NAN rows from fpdffull '''
    fpdffull = fpdffull[np.isfinite(fpdffull['FP'])]
    
    ''' Delete rows with zero for rotation rank '''
    fpdffull = fpdffull[fpdffull.Rank != 0]
                        
                    
    ''' No matter what, save new full dataframe '''
    UpdateFullDF(fppmdffull,mindffull,fpdffull)    
            
    return[fppmdffull,mindffull,fpdffull]

        
#################################UPDATEFULLDF##################################

def UpdateFullDF(fppmdffull,mindffull,fpdffull):
    ''' Rewrite full dataframes '''
    with open("Machine Learning/fppmdffull.p","wb") as handle:
        pickle.dump(fppmdffull,handle)
    with open("Machine Learning/mindffull.p", "wb") as handle:
        pickle.dump(mindffull,handle) 
    with open("Machine Learning/fpdffull.p","wb") as handle:
        pickle.dump(fpdffull,handle)
###################################SETCUTOFF###################################

def SetCutoff(fppmdf,mindf,a,b):
    fppmdf = fppmdf[fppmdf.FPPM > a]
    mindf = mindf[mindf.Min > b]

    return[fppmdf,mindf]  
    
   
##################################DOREGRESSION###############################

def DoRegression(fullX,fullY,newX,islinear,alpha_0):
    if islinear:
      ''' Form linear regression model using fullX, fullY '''
      regr = linear_model.LinearRegression()
      regr.fit(fullX,fullY)
    
      ''' Use model to make predictions on data '''
      predictions = regr.predict(newX)

    else:
      ''' Form ridge regression model using fullX, fullY'''
      regr = linear_model.Ridge(alpha = alpha_0)
      regr.fit(fullX,fullY)
      
      ''' Use model to make predictions on data '''
      predictions = regr.predict(newX)
      
    ''' Print regression coefficients '''
#    print(regr.coef_)
      
    return predictions

################################GETMINERROR#################################

def GetMinError\
(fullminerrordf,mindfX,minerrorfeatures,minerrorresponses,numsteps):
    
    # TEMPORARY CHANGE: ROTATION RANKS ONLY GO UP TO 3
    
    ''' Split dataframe by rotation '''
    fullminerrordf1 = fullminerrordf[fullminerrordf['Rank'] == 1]
    fullminerrordf2 = fullminerrordf[fullminerrordf['Rank'] == 2]
    fullminerrordf3 = fullminerrordf[fullminerrordf['Rank'] >= 3]
#    fullminerrordf3 = fullminerrordf[fullminerrordf['Rank'] == 3]
#    fullminerrordf4 = fullminerrordf[fullminerrordf['Rank'] >= 4]

    ''' Split each rotation spot into features and responses '''
    fullminerrordf1X = fullminerrordf1[minerrorfeatures]
    fullminerrordf1Y = fullminerrordf1[minerrorresponses]
    fullminerrordf2X = fullminerrordf2[minerrorfeatures]
    fullminerrordf2Y = fullminerrordf2[minerrorresponses]
    fullminerrordf3X = fullminerrordf3[minerrorfeatures]
    fullminerrordf3Y = fullminerrordf3[minerrorresponses]
#    fullminerrordf4X = fullminerrordf4[minerrorfeatures]
#    fullminerrordf4Y = fullminerrordf4[minerrorresponses]

    ''' Introduce step size for testing each minerror df for KNN'''
    ttsstepsize1 = math.floor(len(fullminerrordf1)/numsteps)
    ttsstepsize2 = math.floor(len(fullminerrordf2)/numsteps)
    ttsstepsize3 = math.floor(len(fullminerrordf3)/numsteps)
#    ttsstepsize4 = max(math.floor(len(fullminerrordf4)/numsteps),1)
    
    ''' Run k-fold cross validation on each possible n_neighbors and get accuracy '''
#    besterror = [10**10]*4
    besterror = [10**10]*3
#    optimalnneighbors = [0,0,0,0]
    optimalnneighbors = [0,0,0]
    for n in range(1,math.floor(len(fullminerrordf1)/2),ttsstepsize1):
#        print(n)
        knn1 = neighbors.KNeighborsRegressor(n_neighbors = n)    
        currenterror1 = abs(cross_val_score(knn1,fullminerrordf1X,fullminerrordf1Y, \
        cv=10,scoring = 'mean_squared_error').mean())
#        print(currenterror1)
        if currenterror1 <= besterror[0]:
            besterror[0] = currenterror1
            optimalnneighbors[0] = n
    for n in range(1,math.floor(len(fullminerrordf2)/2),ttsstepsize2):
        knn2 = neighbors.KNeighborsRegressor(n_neighbors = n)    
        currenterror2 = abs(cross_val_score(knn2,fullminerrordf2X,fullminerrordf2Y, \
        cv=10,scoring = 'mean_squared_error').mean())
        if currenterror2 <= besterror[1]:
            besterror[1] = currenterror2
            optimalnneighbors[1] = n
    for n in range(1,math.floor(len(fullminerrordf3)/2),ttsstepsize3):
        knn3 = neighbors.KNeighborsRegressor(n_neighbors = n)    
        currenterror3 = abs(cross_val_score(knn3,fullminerrordf3X,fullminerrordf3Y, \
        cv=10,scoring = 'mean_squared_error').mean())
        if currenterror3 <= besterror[2]:
            besterror[2] = currenterror3
            optimalnneighbors[2] = n

    ''' In case rotation spot 4 df is too small '''
#    if len(fullminerrordf4) < 5:
#        nmax4 = len(fullminerrordf4)
#    else:
#        nmax4 = math.floor(len(fullminerrordf4)/2)
#        
#    for n in range(1,nmax4,ttsstepsize4):
#        knn4 = neighbors.KNeighborsRegressor(n_neighbors = n)    
#        currenterror4 = abs(cross_val_score(knn4,fullminerrordf4X,fullminerrordf4Y, \
#        cv=min(10,len(fullminerrordf4)),scoring = 'mean_squared_error').mean())
#        if currenterror4 <= besterror[3]:
#            besterror[3] = currenterror4
#            optimalnneighbors[3] = n
            
    ''' Instantiate KNN regressor with optimal n_neighbors '''
    neigh1 = neighbors.KNeighborsRegressor(n_neighbors = optimalnneighbors[0])
    neigh2 = neighbors.KNeighborsRegressor(n_neighbors = optimalnneighbors[1])
    neigh3 = neighbors.KNeighborsRegressor(n_neighbors = optimalnneighbors[2])
#    neigh4 = neighbors.KNeighborsRegressor(n_neighbors = optimalnneighbors[3])
      
    ''' Fit each minerror dataframe using KNN regressors '''
    neigh1.fit(fullminerrordf1X,fullminerrordf1Y)
    neigh2.fit(fullminerrordf2X,fullminerrordf2Y)
    neigh3.fit(fullminerrordf3X,fullminerrordf3Y)
#    neigh4.fit(fullminerrordf4X,fullminerrordf4Y)
    
    ''' Create dataframe of today's players with integer indices '''
    mindfXint = mindfX.reset_index(drop=True)
    
    ''' Split today's dataframe by depth chart rank, extract feature variables '''
    todaysminerrordfX1 = mindfXint[mindfXint['Rank'] == 1][minerrorfeatures]
    todaysminerrordfX2 = mindfXint[mindfXint['Rank'] == 2][minerrorfeatures]
    todaysminerrordfX3 = mindfXint[mindfXint['Rank'] >= 3][minerrorfeatures]
#    todaysminerrordfX3 = mindfXint[mindfXint['Rank'] == 3][minerrorfeatures]
#    todaysminerrordfX4 = mindfXint[mindfXint['Rank'] >= 4][minerrorfeatures]
    
    ''' Create today's minutes error KNN predictions for each rank '''
    if not todaysminerrordfX1.empty:
        todaysminerrordfY1 = pd.DataFrame(\
        data = neigh1.predict(todaysminerrordfX1), \
        index = todaysminerrordfX1.index.tolist())
    else:
        todaysminerrordfY1 = pd.DataFrame([],[])
    if not todaysminerrordfX2.empty:
        todaysminerrordfY2 = pd.DataFrame(\
        data = neigh2.predict(todaysminerrordfX2), \
        index = todaysminerrordfX2.index.tolist())
    else:
        todaysminerrordfY2 = pd.DataFrame([],[])
    if not todaysminerrordfX3.empty:
        todaysminerrordfY3 = pd.DataFrame(\
        data = neigh3.predict(todaysminerrordfX3), \
        index = todaysminerrordfX3.index.tolist())
    else:
        todaysminerrordfY3 = pd.DataFrame()
#    if not todaysminerrordfX4.empty:    
#        todaysminerrordfY4 = pd.DataFrame(\
#        data = neigh4.predict(todaysminerrordfX4), \
#        index = todaysminerrordfX4.index.tolist())
#    else:
#        todaysminerrordfY4 = pd.DataFrame([],[])
    
    ''' Form single dataframe of minutes error predictions '''
#    todaysminerrordffull = todaysminerrordfY1.append([\
#    todaysminerrordfY2,todaysminerrordfY3,todaysminerrordfY4]).sort_index()
    todaysminerrordffull = todaysminerrordfY1.append([\
    todaysminerrordfY2,todaysminerrordfY3]).sort_index()
    todaysminerrordffull.columns = ['Min Error']
    
    return [todaysminerrordffull,optimalnneighbors]
      
################################EXPORTPROJECTIONSTOCSV##########################

def ExportProjectionsToCSV(todayfilename,expectedscore,MLexpectedscore,MLexpectedscorenew):
    
    ''' Export day's projections (NO MACHINE LEARNING) to CSV file ''' 
    with open("Daily Spreadsheets/FD" + todayfilename + ".csv",'w') as outputfile:
        wr = csv.writer(outputfile, dialect = 'excel')
        for row in expectedscore:
            wr.writerow(row) 
            
    ''' Export machine learning projections to CSV file '''
    with  open("Daily Spreadsheets/FD" + todayfilename + "ML.csv",'w') as outputfile:
        wr = csv.writer(outputfile, dialect = 'excel')
        for row in MLexpectedscore:
            wr.writerow(row)
            
    ''' Export new machine learning projections to CSV file '''
    with open("Daily Spreadsheets/FD" + todayfilename + "MLnew.csv",'w') as outputfile:
        wr = csv.writer(outputfile, dialect = 'excel')
        for row in MLexpectedscorenew:
            wr.writerow(row)


##################################YESTERDAY##################################

def Yesterday():
    ''' Calculate minutes played, FPPM for all \
    eligible players in previous day's games '''
    
    ''' Set up data frame of yesterday's stats '''
    
    yesterdaysurl = "http://www.basketball-reference.com/friv/dailyleaders.cgi"
    
    yesterdayspage = urllib.request.urlopen(yesterdaysurl)
    yesterdayssoup = BeautifulSoup(yesterdayspage.read(),"lxml")
    yesterdaystable = yesterdayssoup.find("table")
    yesterdayscolumnheaders = [th.getText() \
    for th in yesterdaystable.find("tr").findAll("th")[1:]]
    yesterdaysdata_rows = [[td.getText() for td in tr.findAll("td")] \
    for tr in yesterdaystable.findAll("tr")[1:]]
    yesterdaysdf = pd.DataFrame(yesterdaysdata_rows, \
    columns = yesterdayscolumnheaders)
    yesterdaysdf = yesterdaysdf[yesterdaysdf.Player.notnull()]

    ''' Convert minutes column to float '''
    yesterdaysdf['MP'] = \
    yesterdaysdf['MP'].apply(lambda x: float(str(x[:x.index(':')]))\
    + float(str(x[x.index(':')+1:]))/60)    
    
    ''' Create dictionary of yesterday's fantasy points and minutes '''
    yesterdaydict = {player: [MyFunctions.CalculateScore([\
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["PTS"]), \
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["TRB"]), \
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["AST"]), \
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["BLK"]), \
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["STL"]), \
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["TOV"])]), \
    float(yesterdaysdf[yesterdaysdf["Player"] == player]["MP"])]
    for player in yesterdaysdf.Player}
    
    for player in yesterdaydict:
        if yesterdaydict[player][1] != 0:
            yesterdaydict[player] = [yesterdaydict[player][0]/\
            yesterdaydict[player][1],yesterdaydict[player][1]]
    
    yesterdaydf = pd.DataFrame.from_dict(yesterdaydict,orient='index')
    yesterdaydf.columns = ['FPPM','Min']

    return yesterdaydf
    
###################################CHOOSEMODEL##############################    

def ChooseModel(fpdffull):
    
    
#   FOR SORTING: USE THIS LINE LATER WHEN COMPUTING ERROR 
#        ''' Sort dataframe by FPValue attribute '''
#    fpdffullsorted = fpdffull.sort(['FPValue'],ascending=False)

    ''' Set up list of possible model types '''
    tfvec = ['True', 'False']
    alphavec = [0.01,0.1,0.5,1,5,10,100]
    modelvec = [[bool1,False,False,alpha1,alpha2] for bool1 in tfvec for \
                alpha1 in alphavec for alpha2 in alphavec] + [[bool1,True,\
                False,0,alpha2] for bool1 in tfvec for alpha2 in alphavec] + \
                [[bool1,False,True,alpha1,0] for bool1 in tfvec for alpha1 \
                 in alphavec] + [[bool1,True,True,0,0] for bool1 in tfvec]

    ''' Index fpdffull with natural numbers for cross-validation '''
    fpdffullint = fpdffull.reset_index()
    
    ''' Rename columns, split fpdf by features and responses '''
    fpdffullint.columns = ['Name', 'Season FPPM','Last 10 FPPM','H/A FPPM','Days Off FPPM', \
    'Opponent FPPM','Pace','Position Defense','Over/Under','FPPM',\
    'Season Min', 'Last 10 Min', 'H/A Min',  'Days Off Min', 'Opponent Min', \
    'Rank', 'Rotation Binary', 'Injury', 'Adjacent Injury', 'Adjusted Line', \
    'Min', 'FP', 'Salary', 'FPValue']
    fpdffeatures = fpdffullint[['Season FPPM','Last 10 FPPM','H/A FPPM','Days Off FPPM', \
    'Opponent FPPM','Pace','Position Defense','Over/Under','FPPM',\
    'Season Min', 'Last 10 Min', 'H/A Min',  'Days Off Min', 'Opponent Min', \
    'Rank', 'Rotation Binary', 'Injury', 'Adjacent Injury', 'Adjusted Line', \
    'Min']]
    fpdfresponses = fpdffullint[['FP','Salary','FPValue']]
    
    ''' Form lists of fppm and min column headers '''
    fppmheaders = ['Season FPPM', 'Last 10 FPPM', 'H/A FPPM', 'Days Off FPPM',
       'Opponent FPPM', 'Pace', 'Position Defense', 'Over/Under', 'FPPM']
    minheaders = ['Season Min', 'Last 10 Min', 'H/A Min', 'Days Off Min', 'Opponent Min',
       'Rank', 'Rotation Binary', 'Injury', 'Adjacent Injury', 'Adjusted Line',
       'Min']
    baseminheaders = minheaders[:5]
    minerrorheaders = minheaders[7:-1]
    
    ''' Set up 5-fold cross validation '''
    numfolds = 5
    kf = KFold(n=len(fpdffull),n_folds=numfolds,shuffle=True)
    
    ''' Instantiate list for errors by each model '''
    modelerror = [0] * len(modelvec)
    
    for train_index, test_index in kf:
        X_train = fpdffeatures.loc[list(train_index),:]
        X_test = fpdffeatures.loc[list(test_index),:]
        Y_train = fpdfresponses.loc[list(train_index),:]
        Y_test = fpdfresponses.loc[list(test_index),:]
                                   
        for modelnumber in range(0,len(modelvec)):
            fppmallbool = modelvec[modelnumber][0]
            fppmlinearbool = modelvec[modelnumber][1]
            baseminlinearbool = modelvec[modelnumber][2]
            
            ''' Choose appropriate feature columns for FPPM Regression '''
            if fppmallbool:
                X_train_FPPM_features = X_train[fppmheaders[:-1:]]
                X_test_FPPM_features = X_test[fppmheaders[:-1:]]
            else:
                X_train_FPPM_features = X_train[fppmheaders[:-4:] + ['Position Defense']]
                X_test_FPPM_features = X_test[fppmheaders[:-4:] + ['Position Defense']]
            
            ''' Response column for FPPM Regression '''
            X_train_FPPM_responses = X_train['FPPM']
            X_test_FPPM_responses = X_test['FPPM']

            ''' Call function to perform regression on data '''
            if fppmlinearbool:
                fppmpredictions = DoRegression(X_train_FPPM_features, \
                                X_train_FPPM_responses,X_test_FPPM_features, \
                                fppmlinearbool,0)
            else:
                    FPPM_alpha_0 = modelvec[modelnumber][3]
                    fppmpredictions = DoRegression(X_train_FPPM_features,\
                    X_train_FPPM_responses,X_test_FPPM_features,\
                    fppmlinearbool,FPPM_alpha_0)
                    
            ''' Choose appropriate feature columns for Basemin Regression '''
            X_train_basemin_features = X_train[baseminheaders]
            X_test_basemin_features = X_test[baseminheaders]
            
            ''' Create new minutes df of rows unaffected by injuries, adjusted line '''
            no_injury_X_train = X_train[X_train['Injury'] + \
                                        X_train['Adjacent Injury'] == 0]
            no_injury_no_line_X_train = no_injury_X_train\
            [abs(no_injury_X_train['Adjusted Line']) < 1]
            basemindfX = no_injury_no_line_X_train[baseminheaders]
            basemindfY = no_injury_no_line_X_train[['Min']] 

            ''' Make base minutes prediction for train and test dataframes '''
            if baseminlinearbool:
                fullbasemin = DoRegression\
                    (basemindfX,basemindfY,X_train[baseminheaders],\
                     baseminlinearbool,0)
                baseminpredictions = DoRegression\
                    (basemindfX,basemindfY,X_test_basemin_features,\
                     baseminlinearbool,0)
            else:
                min_alpha_0 = modelvec[modelnumber][4]
                fullbasemin = DoRegression\
                    (basemindfX,basemindfY,X_train[baseminheaders],\
                     baseminlinearbool,min_alpha_0)
                baseminpredictions = DoRegression\
                    (basemindfX,basemindfY,X_test_basemin_features,\
                     baseminlinearbool,min_alpha_0)
                    
            ''' Column for minutes adjustments '''
            minerrorresponses = ['Min Error']

            ''' Create dataframe to calculate change from basemin based on line ''' 
            minerror = X_train.Min-fullbasemin.reshape(1,-1).tolist()[0]
            fullminerrordf = X_train
            fullminerrordf['Min Error'] = minerror
                                   
            ''' Predict X_test's min error using function call '''
            [X_test_minerrordffull,optimalnneighbors] = \
            GetMinError\
            (fullminerrordf,X_test,minerrorheaders,minerrorresponses,10)

            ''' Calculate FP predictions '''         
            fppmpredictlist = fppmpredictions.tolist()
            baseminlist = [element[0] for element in baseminpredictions.tolist()]
            minerrorlist = X_test_minerrordffull['Min Error'].tolist()
            X_test_predict = [fppmpredictlist[i] * (baseminlist[i] + \
                              minerrorlist[i]) for i in range(0,len(X_test))]
                              
            ''' Create dataframe containing predictions '''
            Y_test['Predicted FP'] = X_test_predict
            errorvec = (Y_test['Predicted FP'] - Y_test['FP']).tolist()
            
            ''' Determine weights based on FPValue '''
            FPmean = np.mean(Y_test.FPValue)
            maxFPdeviation = max(Y_test.FPValue - FPmean)
            minFPdeviation = min(Y_test.FPValue - FPmean)
            maxweight = 5
            minweight = 1/5                                   
            weights = [1 + (maxweight - 1) * ((element - FPmean) / maxFPdeviation) \
                       if element >= FPmean \
                       else 1 - (1 - minweight) * ((element - FPmean) / minFPdeviation) \
                       for element in Y_test.FPValue.tolist()]
            
                               
            ''' Calculate weighted norm error of predictions, add to list '''
            currenterror = ModifiedErrorNorm(errorvec,weights)
            modelerror[modelnumber] += currenterror

        print("weights are",weights)
        
    ''' Divide by number of folds to determine average error for each model '''    
    averageerror = [modelerror[i]/numfolds for i in range(0,len(modelvec))]
                    
#    ''' Display errors and settings of each model type'''
#    for i in range(0,len(modelvec)):
#        print("fppmallbool: ",modelvec[i][0]," fppmlinearbool: ",modelvec[i][1], \
#              " baseminlinearbool: ",modelvec[i][2], " alpha1: ",modelvec[i][3], \
#              " alpha2: ", modelvec[i][4])
#        print("Resulting error: ", averageerror[i])

    ''' Get index of lowest error model and display '''
    imin = np.argmin(averageerror)
    print("Optimal model is ",modelvec[imin], "with an error of ",averageerror[imin])
     
    return [modelvec[imin],fppmheaders,minheaders]

##################################MODIFIEDNORM###############################

def ModifiedErrorNorm(errorvec,weights):
    
    
    error = math.pow(sum([weights[i] * math.pow(errorvec[i],2) \
                for i in range(0,len(errorvec))]),1/2)
    
    return error
    
    
##################################RUNNEWMODEL###############################

def RunNewModel(playernamelist,fpdffull,fppmdfX,mindfX,newfppmheaders,newminheaders,\
                fppmallbool,fppmlinearbool,baseminlinearbool,alpha1,alpha2):
    
    ''' Rename columns of today's dataframe '''
    fpdffull.columns = newfppmheaders + newminheaders + ['FP','Salary','FPValue']
    fppmdfX.columns = newfppmheaders[:-1:]
    mindfX.columns = newminheaders[:-1:]

    ''' Split minheaders into basemin and minerror headers '''
    baseminheaders = newminheaders[:5]
    minerrorheaders = newminheaders[7:-1]
    
    
    ''' Choose appropriate feature columns for FPPM Regression '''
    if fppmallbool:
        full_FPPM_features = fpdffull[newfppmheaders[:-1:]]
        today_FPPM_features = fppmdfX
    else:
        full_FPPM_features = fpdffull[newfppmheaders[:-4:] + ['Position Defense']]
        today_FPPM_features = fppmdfX[newfppmheaders[:-4:] + ['Position Defense']]
    
    ''' Response column for FPPM Regression '''
    full_FPPM_responses = fpdffull['FPPM']

    ''' Call function to perform regression on data '''
    if fppmlinearbool:
        fppmpredictions = DoRegression(full_FPPM_features, \
                        full_FPPM_responses,today_FPPM_features, \
                        fppmlinearbool,0)
    else:
            FPPM_alpha_0 = alpha1
            fppmpredictions = DoRegression(full_FPPM_features,\
            full_FPPM_responses,today_FPPM_features,\
            fppmlinearbool,FPPM_alpha_0)
            
    ''' Choose appropriate feature columns for Basemin Regression '''
    full_basemin_features = fpdffull[baseminheaders]
    today_basemin_features = mindfX[baseminheaders]
    
    ''' Create new minutes df of rows unaffected by injuries, adjusted line '''
    no_injury_full = fpdffull[fpdffull['Injury'] + \
                                fpdffull['Adjacent Injury'] == 0]
    no_injury_no_line_full = no_injury_full\
    [abs(no_injury_full['Adjusted Line']) < 1]
    basemindfX_full = no_injury_no_line_full[baseminheaders]
    basemindfY_full = no_injury_no_line_full[['Min']] 

    ''' Make base minutes prediction for train and test dataframes '''
    if baseminlinearbool:
        fullbasemin = DoRegression\
            (basemindfX_full,basemindfY_full,full_basemin_features,\
             baseminlinearbool,0)
        baseminpredictions = DoRegression\
            (basemindfX_full,basemindfY_full,today_basemin_features,\
             baseminlinearbool,0)
    else:
        min_alpha_0 = alpha2
        fullbasemin = DoRegression\
            (basemindfX_full,basemindfY_full,full_basemin_features,\
             baseminlinearbool,min_alpha_0)
        baseminpredictions = DoRegression\
            (basemindfX_full,basemindfY_full,today_basemin_features,\
             baseminlinearbool,min_alpha_0)
            
    ''' Column for minutes adjustments '''
    minerrorresponses = ['Min Error']

    ''' Create dataframe to calculate change from basemin based on line ''' 
    minerror = fpdffull.Min-fullbasemin.reshape(1,-1).tolist()[0]
    fullminerrordf = fpdffull.copy()
    fullminerrordf['Min Error'] = minerror
                           
    ''' Predict X_test's min error using function call '''
    [today_minerrordffull,optimalnneighbors] = \
    GetMinError\
    (fullminerrordf,mindfX,minerrorheaders,minerrorresponses,10)

    ''' Calculate FP predictions '''         
    fppmpredictlist = fppmpredictions.tolist()
    baseminlist = [element[0] for element in baseminpredictions.tolist()]
    minerrorlist = today_minerrordffull['Min Error'].tolist()
    FP_predict = [fppmpredictlist[i] * (baseminlist[i] + \
                      minerrorlist[i]) for i in range(0,len(mindfX))]
    
    FP_predict_dict = {playernamelist[i]: FP_predict[i] for i in range(0,len(playernamelist))}
                  
    return FP_predict_dict
                      
  

# ANOTHER OPTION: MODIFY NORM TO MINIMIZE IN MINERROR KNN
