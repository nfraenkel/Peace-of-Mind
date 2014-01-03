#!/usr/local/bin/python

# to use Virtual Env !flask/bin/python
'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
http://flask.pocoo.org/docs/quickstart/
http://flask-restful.readthedocs.org/en/latest/

V1.2 replaces the iterative withdrawal computation with a straight calculation, since the relationship Return Rate -> Withdrawal is linear
V2 Use MonteCarlo simulation - and compute the withdrawal amounts based on individual Return Rates for each year - in V2 we use the Default values for Pre- as well as Retirement
V2.1 FinPlan is now a sequence of investment phases, where a phase includes:
- Name [Optional]
- startAge
- endAge
- NetContribution: Positive if it is added to the account, negative if it is a withdrawal
- ToCompute: True if the withdrawal for that Phase is to be computed - in which case NetContribution is ignored
    If more than 1 phase have "ToCompute" set to True, the same amount will be applied to each phase
- Portfolio: a Dict of Portfolio and their respective percentage allocation e.g. Portfolio = {"Stocks": 50.0, "Bonds": 35.0, "T-Bills": 15.0, "Cash": 0.0}
RULES:
- Phases must be continuous i.e. the EndAge of one phase must be the StartAge of the next phase
- Portfolio allocation must be <= 100% - if less than 100%, then the remainder is allocated to Cash 
'''

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.views import MethodView
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
import uuid
import locale
import math
import string
import numpy as np
import numpy.random as rand
import sys

app = Flask(__name__)
api = Api(app)

# Default Values
DefaultEndFunds = 1.0 # Default value for target end funds at end of retirement
DefaultNbRun = 10000
DefaultMeanRate = 8.680291  # Per S&P 500 history
DefaultStddevRate = 16.191388   # Per S&P 500 history
DefaultSuccessRatio = 90 # % between 0-100

'''
From: http://fc.standardandpoors.com/sites/client/generic/axa/axa4/Article.vm?topic=5991&siteContent=8088 
Total Returns From 1926-2013*
     Stocks    Bonds    T-Bills
Annualized Return    9.9%    5.8%    3.6%
Best Year    60.0 (1935)    42.1 (1982)    14.0 (1981)
Worst Year    -41.1 (1931)    -12.2 (2009)    0.0 (1940)
Standard Deviation    19.1    7.5    0.9
'''
HistoricalReturns = {"Stocks": [9.90, 19.1], "Bonds": [5.80, 7.50], "T-Bills": [3.60, 0.90], "Cash": [0.0, 0.0]}


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
            'endAge': 60,   # On purpose to trigger error - should be 65
            'NetContribution': 0,
            'ToCompute': True,
            'Portfolio': {"Stocks": 60.0, "Bonds": 40.0, "T-Bills": 0.0, "Cash": 10.0}},
            {'Name': 'Working',
            'startAge': 30,
            'endAge': 55,
            'NetContribution': 10000,
            'ToCompute': False,
            'Portfolio': {"Stocks": 80.0, "Bonds": 20.0, "T-Bills": 0.0, "Cash": 0.0}}],
        'InflationRate': 2.0        
    }
]


# ------------------
def main(argv):
    
    for finplan in FinPlanScenario:
        phaseList = finplan['Phase']
        phaseList.sort(key=lambda phase: phase['startAge'])
        for phase in phaseList:
            print('Phase: %s - StartAge: %d' % (phase['Name'], phase['startAge']))
        # Make sure the phases are continuous
        endAge = phaseList[0]['endAge']
        for phase in phaseList[1:]:
            if phase['startAge'] != endAge:
                print('Phases need to be continuous - endAge (%d) is not equal to startAge(%d) of next' % (endAge, phase['startAge']))
                exit(1)
            else:
                endAge = phase['endAge']
            
    exit(0)
        
        

# ------------------
if __name__ == '__main__':
    main(sys.argv[1:])
