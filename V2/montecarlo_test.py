#!/usr/local/bin/python

'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
http://flask.pocoo.org/docs/quickstart/
http://flask-restful.readthedocs.org/en/latest/

Computes the amount of $$ that can be withdrawn during retirement - using Monte-Carlo simulations
All inputs are within the program
A scenario includes a number of phases (e.g. working, semi-retirement, retirement)
Each phase has a portfolio allocation of asset types (stocks, bonds, etc), and a contribution (negative for withdrawal). 
If the "ToCompute" flag is set in a phase, then the contribution (in this case withdrawal) will be computed by the MC simulations.
More that one phase can set ToCompute, but all these phases will share the same computed contribution
The MC simulations use the Historical mean,stddev for each asset class - and generate random rate of returns using a normal distribution based on the mean/stddev of the given asset class
The simulations are run "NbRun" and the contribution amount is returned based on the confidence factor 
'''

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.views import MethodView
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
import uuid
import math
import string
import numpy as np
import numpy.random as rand
from numpy.core.numeric import dtype
import sys
import json

app = Flask(__name__)
api = Api(app)

# Default Values
DefaultEndFunds = 1.0 # Default value for target end funds at end of retirement
DefaultNbRun = 1000
DefaultConfidenceFactor = 90 # % between 0-100
Debug = False

'''
From: http://fc.standardandpoors.com/sites/client/generic/axa/axa4/Article.vm?topic=5991&siteContent=8088 
Total Returns From 1926-2013*
     Stocks    Bonds    T-Bills
Annualized Return    9.9%    5.8%    3.6%
Best Year    60.0 (1935)    42.1 (1982)    14.0 (1981)
Worst Year    -41.1 (1931)    -12.2 (2009)    0.0 (1940)
Standard Deviation    19.1    7.5    0.9
'''
HistoricalReturn = {"Stocks": [9.90, 19.1], "Bonds": [5.80, 7.50], "T-Bills": [3.60, 0.90], "Cash": [0.0, 0.0]}


# Default Values
# Declare it in a single dict - this way, we only have to maintain it here - the rest of the code should just iterate the dict
DefaultFinPlanValue = {
    'AgeToday': 30, 
    'AgeRetirement': 65,
    'AgeEnd': 90,
    'StartingAmount': 200000,
    'PreContribution': 17500,
    'PreReturnRate': 7.0,
    'RetirementReturnRate': 5.0,
    'InflationRate': 2.0
    }

# Populate the Array of Financial Plans with Initial Values
# ** Make sure that the required and DEFAULT attributes are all there (not necessarily w/ default values 
FinPlanScenario = [
    {
        'FinPlan_ID': '445585fb-5c9d-4254-9b91-0197a584e6ba',
        'UserName': 'Lucky',
        'Title': 'Conservative',
        'Description': 'Conservative Scenario', 
        'Email': 'SantaClaus@xmas.com',
        'HasResult': False,
        'AgeToday': 30, 
        'AgeRetirement': 65,
        'AgeEnd': 90,
        'StartingAmount': 200000,
        'Phase' : [
            {'Name': 'Working',
            'startAge': 30,
            'endAge': 65,
            'NetContribution': 17500,
            'ToCompute': False,
            'Portfolio': {"Stocks": 80.0, "Bonds": 20.0, "T-Bills": 0.0, "Cash": 0.0}},
            {'Name': 'Retired',
            'startAge': 65,
            'endAge': 90,
            'NetContribution': 0,
            'ToCompute': True,
            'Portfolio': {"Stocks": 50.0, "Bonds": 30.0, "T-Bills": 10.0, "Cash": 10.0}}],
      'InflationRate': 3.0    },
    {
        'FinPlan_ID': '388774d0-fd92-468c-b2cf-49039ce5c6ce',
        'UserName': 'Chance',
        'Title': 'Aggressive',
        'Description': 'Aggressive Scenario', 
        'Email': 'SantaClaus@xmas.com',
        'HasResult': False,
        'AgeToday': 30, 
        'AgeRetirement': 65,
        'AgeEnd': 90,
        'StartingAmount': 200000,
        'Phase' : [
            {'Name': 'Retired',
            'startAge': 65,
            'endAge': 90,
            'NetContribution': 0,
            'ToCompute': True,
            'Portfolio': {"Stocks": 50.0, "Bonds": 30.0, "T-Bills": 10.0, "Cash": 10.0}},
            {'Name': 'Semi-Retired',
            'startAge': 55,
            'endAge': 65, 
            'NetContribution': 0,
            'ToCompute': True,
            'Portfolio': {"Stocks": 60.0, "Bonds": 40.0, "T-Bills": 0.0, "Cash": 10.0}},
            {'Name': 'Working',
            'startAge': 30,
            'endAge': 55,
            'NetContribution': 17500,
            'ToCompute': False,
            'Portfolio': {"Stocks": 80.0, "Bonds": 20.0, "T-Bills": 0.0, "Cash": 0.0}}],
        'InflationRate': 2.0        
    }
]
# Info on nested fields: http://flask-restful.readthedocs.org/en/latest/fields.html#nested-field

portfolio_fields = {
    "Stocks": fields.Float,
    "Bonds": fields.Float,
    "T-Bills":fields.Float,
    "Cash": fields.Float
}        

phase_fields = {
    'Name': fields.String,
    'startAge': fields.Float,
    'endAge': fields.Float,
    'NetContribution': fields.Float,
    'ToCompute': fields.Boolean,
    'Portfolio': fields.Nested(portfolio_fields)
}

finplan_fields = {
    'FinPlan_ID': fields.String,
    'Title': fields.String,
    'Description': fields.String,
    'UserName': fields.String,
    'Email': fields.String,
    'HasResult': fields.Boolean,
    'AgeToday': fields.Float,
    'AgeRetirement': fields.Float,
    'AgeEnd': fields.Float,
    'StartingAmount': fields.Float,
    'InflationRate': fields.Float,
    'Withdrawal':fields.Float 
}

# ------------------
def run_1_year(StartFunds, return_rate, contribution):
    '''
    Compute funds at end of year based on:
    - starting funds
    - interest rate as a float
    - withdrawal taken at START of year
    '''
    if contribution >=0:  # add contribution at end of year
        EndFunds = (1.0 + return_rate) * StartFunds + contribution
    else:  # withdraw the (negative) contribution at start of year
        EndFunds = (1.0 + return_rate) * (StartFunds + contribution)
    return (EndFunds)

# ------------------
def run_all_years_v2(ContributionAmount, finPlan, rateArray):
    
    StartFunds = finPlan['StartingAmount']
    inflationRate = float(finPlan['InflationRate']) * 0.01
    inflationContribution = ContributionAmount  # will be adjusted yearly by inflation amount
    phaseList = finPlan['Phase']
    
    yr = 0 # goes from 0 to (finPlan['AgeEnd'] - finPlan['AgeToday'] -1)    
    phaseList.sort(key=lambda phase: phase['startAge'])  # make sure the phases are in order
    for phase in phaseList:
        inflationContribution *= (1+inflationRate)  # adjust for inflation every year
        computeFlag = phase['ToCompute']
        phaseYear= phase['endAge'] - phase['startAge']  # number of years in this phase
        for x in range(phaseYear):
            returnRate = rateArray[yr] * 0.01  # scale to a number (from percentage)
            if computeFlag:  # Use the contribution passed as argument, adjusted for inflation
                contribution = inflationContribution
            else: # Use what the user specified
                contribution = phase['NetContribution']
            EndFunds = run_1_year(StartFunds, returnRate, contribution)   # Use the return rate specified for that year
            if Debug:                        
                print ('Year:  {:,}: start = $ {:,} - end = ${:,} - rate = {:f}%  contribution = ${:.2f}'.format(yr,int(StartFunds), int(EndFunds), 100.0 * returnRate, contribution))
            StartFunds = EndFunds
            yr += 1
            
    return(EndFunds)

# ------------------
def compute_withdrawal_v2(targetEndValue, finPlan, rateArray):    
    '''
    For a given interest rate, find the withdrawal amount so that the EndFunds are equal to the targetEndValue
    In other words, what withdrawals can we afford based on interest rate?
    Version 2: the relationship between EndFunds and withdrawal is linear => compute Endfunds for 2 values and interpolate to get the results
    '''
    withdrawal_1 = 0
    withdrawal_2 = 100000
        
    EndFunds_1 = run_all_years_v2(withdrawal_1, finPlan, rateArray)
    EndFunds_2 = run_all_years_v2(withdrawal_2, finPlan, rateArray)
    A_Cst = (EndFunds_2 - EndFunds_1) / (withdrawal_2 - withdrawal_1)
    B_Cst = EndFunds_1 - A_Cst * withdrawal_1
    withdrawal = (targetEndValue - B_Cst) / A_Cst
    lastEndFunds = run_all_years_v2(withdrawal, finPlan, rateArray)
    
    return (withdrawal, lastEndFunds)
   
# ------------------
def findSuccess(inList, ratio, negativeFlag = False):
    
    '''
    Find the value in the list such that 'ratio' % of the items in the list are smaller than it
    List is a list of float or int
    ratio is a % - between 0 and 100 
    negativeFlag (optional) should be set to True, if all elements in the list are negative
    '''
        
    # Sort the list
    if (not negativeFlag): # All values in the list are positive
        inList.sort(reverse=True)  # Most optimistic/positive scenario first
    else: 
        inList.sort()  # Largest negative value first
    # find the item that is small enough to succeed in ConfidenceFactor % of cases
    limitCnt = int (len(inList) * ratio * 0.01) - 1  # ConfidenceFactor is a %, account for index starting at 0
    if (limitCnt < 0):
        limitCnt = 0
    elif(limitCnt > len(inList) -1):
        limitCnt = len(inList) -1
    return (inList[limitCnt])

# ------------------
def RunScenario(finPlan):
    '''
    Computes a Financial Plan based on the parameters of the plan
    Returns a Withdrawal value and set HasResult to True
    '''
    
    withdrawal, EndFunds = compute_withdrawal(DefaultEndFunds, finPlan)
    
    finPlan['Withdrawal'] = withdrawal # to show the result
    finPlan['HasResult'] = True
    return(finPlan)

# ------------------
def computeRate(phaseList, HistoricalReturn):
    
    '''
    Create an array of rates for each year.
    For a given year, the rate is the weighted rate for each class of asset
    The rate of a given asset is generated from a normal distribution, given its mean and stddev stored in Historical assets.
    For ease of programming, we iterate over each asset class on the outer loop
    The return values are float percentages - e.g 8.05 (%) - will need to be scaled by 1/100
    '''

    # Assume that the phaseList is sorted and that the phases ore continuous
    NbYear = phaseList[-1]['endAge'] - phaseList[0]['startAge']
    startYear = phaseList[0]['startAge']
    returnArray=np.zeros(NbYear, dtype=np.float64)
    for asset, statList in HistoricalReturn.iteritems():
        if (asset == 'Cash'):
            continue   # Cash has 0 return
        phaseIndx = 0
        rateArray = np.random.normal(statList[0],statList[1], size = NbYear)
        for yr in range( NbYear):
            returnArray[yr] += rateArray[yr] * (0.01 * phaseList[phaseIndx]['Portfolio'][asset]) # weight by % allocation for this asset type
            # print ('yr: %d - phaseIndx: %d - asset: %s - asset %%: %.2f  asset_rate: %.2f%%' % (yr, phaseIndx, asset,phaseList[phaseIndx]['Portfolio'][asset], rateArray[yr] ))
            yr += 1
            if yr+startYear == phaseList[phaseIndx]['endAge']:  # go to the next phase
                phaseIndx += 1
    
    return(rateArray)          

# ------------------
def MonteCarlo_v2(finPlan, NbRun,ConfidenceFactor):
    '''
    For each of NbRun
    compute an array of Return Rates for each portfolio type for each year, and add this to the compound rate - proportional to the portfolio allocation
    Based on the return rates, compute the withdrawal amount for this sequence of rates
    Keep all the individual results, rank them, and pick the one that will meet the success ratio - i.e. that is small enough that it will generate EndFunds larger than the target 
    Successratio-% of the time (i.e. runs)
    '''
    
    phaseList = finPlan['Phase']
    phaseList.sort(key=lambda phase: phase['startAge'])
    # Assume that phases have been checked and that they are continuous
    withdrawalList =[]
    rateList =[]
    run = 0
    targetEndFunds = finPlan.get('TargetEndFunds', DefaultEndFunds)
    while (run < NbRun):
        # generate a list of Return Rates based on the mean & stddev
        rateArray = computeRate(phaseList, HistoricalReturn)        
        withdrawal, EndFunds = compute_withdrawal_v2(DefaultEndFunds, finPlan,rateArray)  
        withdrawalList.append(withdrawal)  # add the results to the list
        # print ('run {:,}: withdrawal ${:,}'.format(run, int(withdrawal)))
        run += 1
        # For testing
        for rate in rateArray:
            rateList.append(rate) 
               
    withdrawalResult = findSuccess(withdrawalList, ConfidenceFactor, True)  # Set NegativeFlag since all values are negative
    # Store the results
    for phase in phaseList:
        if phase['ToCompute']: # update the result and lower the flag
            phase['netContribution'] = withdrawalResult # enter the result
            phase['ToCompute'] = False
    finPlan['HasResult'] = True
    
    minWithdrawal = min(withdrawalList)
    maxWithdrawal = max(withdrawalList)    
    # Note max & min are "inverted" since withdrawal is a negative number
    print('Result = ${:,} - Max = ${:,} - Min = ${:,}'.format(int(-withdrawalResult), int(-minWithdrawal),int(-maxWithdrawal)))
    # compute mean and stddev from the rateList
    retArray = np.array(rateList, dtype=np.float64)
    mean = np.mean(retArray, dtype=np.float64)
    stddev = np.std(retArray, dtype=np.float64) 
    print ('Rate: mean = %f  stddev = %f ' % (mean, stddev))
    

    return(finPlan)  

# ------------------
def checkFinPlan(finplan):
    phaseList = finplan['Phase']
    phaseList.sort(key=lambda phase: phase['startAge'])
    for phase in phaseList:
        print('Phase: %s - StartAge: %d' % (phase['Name'], phase['startAge']))
    # Make sure the phases are continuous
    endAge = phaseList[0]['endAge']
    for phase in phaseList[1:]:
        if phase['startAge'] != endAge:
            errStr = ('Phases need to be continuous - endAge (%d) is not equal to startAge(%d) of next' % (endAge, phase['startAge']))
            return(True, errStr)
        else:
            endAge = phase['endAge']
    if finplan['AgeToday'] != phaseList[0]['startAge']:
        errStr = 'Age today (%d) is different from the starting age of the first Phase (%d)' % (finplan['AgeToday'], phaseList[0]['startAge'])
        return(True, errStr)
    if finplan['AgeEnd'] != phaseList[-1]['endAge']:
        errStr = ' End Age  (%d) is different from the end age of the last Phase (%d)' % (finplan['AgeEnd'] , phaseList[-1]['endAge'])        
        return(True, errStr)
    # Make sure that in each phase, the portfolio allocation adds up to 100% - If not, then adjust the cash - if cannot adjust the cash -> error
    for phase in phaseList:
        totalPct = 0.0
        portfolio = phase['Portfolio']
        print(portfolio)
        for portf in portfolio:  # compute sum of % of asset allocations for this phase
            totalPct += float(portfolio[portf])
        if totalPct == 100.0:
            continue # we're good
        else:
            delta = 100.0 - totalPct
            # Attempt to adjust the Cash allocation
            newCashPct = portfolio.get('Cash', 0) + delta  # adjust the Cash allocation
            if (newCashPct >= 0.0 and newCashPct <= 100.0):  # new Cash allocation is within bounds
                portfolio['Cash'] = newCashPct # adjust Cash allocation
                print('Fixed Portfolio', phase['Portfolio'])
            else:  # Can't fix things -> error
                errStr = 'Portfolio allocations do not add up to 100% in one of the phases'       
                return(True, errStr)   
    
    return (False,"it's all good")  # no errors

# ------------------
def main(argv):
    
    for finplan in FinPlanScenario:
        errorFlag, errorString = checkFinPlan(finplan)
        if errorFlag:
            print(errorString)
            exit (-2)  # return an error response

                
    for finplan in FinPlanScenario:
        resultPlan = MonteCarlo_v2(finplan, DefaultNbRun, DefaultConfidenceFactor)  # only 1 run to test
        print json.dumps(resultPlan, sort_keys=True, indent=4)
            
    exit(0)
        
        

# ------------------
if __name__ == '__main__':
    main(sys.argv[1:])
