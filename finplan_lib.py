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
More that one phase can set ToCompute, but all these phases will share the same value in NetContribution
The MC simulations use the Historical mean,stddev for each asset class - and generate random rate of returns using a normal distribution based on the mean/stddev of the given asset class
The simulations are run "NbRun" and the contribution amount is returned based on the confidence factor 
'''

import numpy as np
from numpy.core.numeric import dtype
import numpy.random as rand
import string


# ToDo: Replace the following default values by arguments - or config variables
# Default Values
Debug = False

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
def run_all_years(ContributionAmount, finPlan, rateArray):
    
    StartFunds = finPlan['StartingAmount']
    inflationRate = float(finPlan['InflationRate']) * 0.01
    inflationContribution = ContributionAmount  # will be adjusted yearly by inflation amount
    phaseList = finPlan['PhaseList']
    
    yr = 0 # goes from 0 to (finPlan['AgeEnd'] - finPlan['AgeToday'] -1)    
    phaseList.sort(key=lambda phase: phase['startAge'])  # make sure the phases are in order
    for phase in phaseList:
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
            inflationContribution *= (1+inflationRate)  # adjust for inflation every year
            yr += 1
            
    return(EndFunds)

# ------------------
def compute_withdrawal(finPlan, rateArray):    
    '''
    For a given interest rate, find the withdrawal amount so that the EndFunds are equal to the TargetEndFunds in the plan
    In other words, what withdrawals can we afford based on interest rate?
    Version 2: the relationship between EndFunds and withdrawal is linear => compute Endfunds for 2 values and interpolate to get the results
    '''
    withdrawal_1 = 0
    withdrawal_2 = 100000
        
    EndFunds_1 = run_all_years(withdrawal_1, finPlan, rateArray)
    EndFunds_2 = run_all_years(withdrawal_2, finPlan, rateArray)
    A_Cst = (EndFunds_2 - EndFunds_1) / (withdrawal_2 - withdrawal_1)
    B_Cst = EndFunds_1 - A_Cst * withdrawal_1
    withdrawal = (finPlan['TargetEndFunds'] - B_Cst) / A_Cst
    lastEndFunds = run_all_years(withdrawal, finPlan, rateArray)
    
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
        rateArray = np.random.normal(statList[0],statList[1], size = NbYear)
        phaseIndx = 0
        alloc = phaseList[phaseIndx]['Portfolio'][asset]  # get the % of asset allocation for the very first phase
        endAge = phaseList[phaseIndx]['endAge']  # age at the end of the very first phase
        for yr in range( NbYear):
            returnArray[yr] += rateArray[yr] * (0.01 * alloc) # weight by % allocation for this asset type
            # print ('yr: %d - phaseIndx: %d - asset: %s - asset %%: %.2f  asset_rate: %.2f%%' % (yr, phaseIndx, asset,phaseList[phaseIndx]['Portfolio'][asset], rateArray[yr] ))
            yr += 1
            if yr+startYear == endAge:  # go to the next phase
                phaseIndx += 1
                if phaseIndx < len(phaseList):
                    alloc = phaseList[phaseIndx]['Portfolio'][asset]  # Update the allocation to match the new phase
                    endAge = phaseList[phaseIndx]['endAge']  # age at the end of the new phase
    
    return(rateArray)          

# ------------------
def MonteCarlo(finPlan, NbRun,ConfidenceFactor, HistoricalReturn):
    '''
    For each of NbRun
    compute an array of Return Rates for each portfolio type for each year, and add this to the compound rate - proportional to the portfolio allocation
    Based on the return rates, compute the withdrawal amount for this sequence of rates
    Keep all the individual results, rank them, and pick the one that will meet the success ratio - i.e. that is small enough that it will generate EndFunds larger than the target 
    Successratio-% of the time (i.e. runs)
    '''
    
    phaseList = finPlan['PhaseList']
    phaseList.sort(key=lambda phase: phase['startAge'])
    # Assume that phases have been checked and that they are continuous
    withdrawalList =[]
    rateList =[]
    run = 0
    targetEndFunds = finPlan['TargetEndFunds']
    while (run < NbRun):
        # generate a list of Return Rates based on the mean & stddev
        rateArray = computeRate(phaseList, HistoricalReturn)        
        withdrawal, EndFunds = compute_withdrawal(finPlan,rateArray)  
        withdrawalList.append(withdrawal)  # add the results to the list
        # print ('run {:,}: withdrawal ${:,}'.format(run, int(withdrawal)))
        run += 1
        # For testing
        for rate in rateArray:
            rateList.append(rate) 
               
    withdrawalResult = findSuccess(withdrawalList, ConfidenceFactor, True)  # Set NegativeFlag since all values are negative
    # Store the results
    for phase in phaseList:
        if phase['ToCompute']: # update the result 
            phase['NetContribution'] = float(0.01 * int(100 * withdrawalResult)) # enter the result - round to 2 decimals
    finPlan['HasResult'] = True
    
    minWithdrawal = min(withdrawalList)
    maxWithdrawal = max(withdrawalList)    
    # Note max & min are "inverted" since withdrawal is a negative number
    print('Result = ${:,} - Max = ${:,} - Min = ${:,}  Nb Runs = {:,}'.format(int(-withdrawalResult), int(-minWithdrawal),int(-maxWithdrawal), NbRun))
    # compute mean and stddev from the rateList
    retArray = np.array(rateList, dtype=np.float64)
    mean = np.mean(retArray, dtype=np.float64)
    stddev = np.std(retArray, dtype=np.float64) 
    print ('Rate: mean = %f  stddev = %f ' % (mean, stddev))

    return  

# ------------------


