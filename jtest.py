#!/usr/local/bin/python

'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
http://flask.pocoo.org/docs/quickstart/
http://flask-restful.readthedocs.org/en/latest/

Tests the passing of scenarios via HTTP REST API - to make sure that the Json structures are correct

NOTE: for the time being, the PhaseList has to be passed monolithically in the PUT command. This is the only way to allow editing or deleting a phase
'''

from flask import Flask, jsonify, abort, request, make_response, url_for
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


# Populate the Array of Financial Plans with Initial Values
# ** Make sure that the required and DEFAULT attributes are all there (not necessarily w/ default values  
# 
# Default Values
# Declare it in a single dict - this way, we only have to maintain it here - the rest of the code should just iterate the dict
DefaultFinPlanValue = {
    'AgeToday': 30, 
    'AgeEnd': 90,
    'InflationRate': 2.0
}

FinPlanScenario = [
    {
        'FinPlan_ID': '445585fb-5c9d-4254-9b91-0197a584e6ba',
        'UserName': 'Lucky',
        'Title': 'Conservative',
        'Description': 'Conservative Scenario', 
        'Email': 'SantaClaus@xmas.com',
        'HasResult': False,
        'AgeToday': 30, 
        'AgeEnd': 90,
        'StartingAmount': 200000,
        'PhaseList' : [
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
        'AgeEnd': 90,
        'StartingAmount': 200000,
        'PhaseList' : [
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
    'UserName': fields.String,
    'Title': fields.String,
    'Description': fields.String,
    'Email': fields.String,
    'HasResult': fields.Boolean,
    'AgeToday': fields.Float,
    'AgeEnd': fields.Float,
    'StartingAmount': fields.Float,
    'PhaseList': fields.List(fields.Nested(phase_fields)),
    'InflationRate': fields.Float    
}

# ------------------
def FinPlanIsOK(finplan):
    '''
    Validates that the finplan passed as argument is OK syntactically
    Returns 2 arguments: Flag + ErrorString. Flag is True if the plan is OK (in which case Error String can be ignored)
    '''
    
    # ToDo: Perform validation of the fields other than those in PhaseList:  e.g. All required fields present, Age >=0 Inflation rate >= 0.0
    
    if (finplan.get('PhaseList') == None):
        return (True,"it's all good")  # no errors

    # Check validity of the phases in PhaseList
    phaseList = finplan['PhaseList']
    phaseList.sort(key=lambda phase: phase['startAge'])

    # Make sure the phases are continuous
    endAge = phaseList[0]['endAge']
    for phase in phaseList[1:]:
        if phase['startAge'] != endAge:
            errStr = ('Phases need to be continuous - endAge (%d) is not equal to startAge(%d) of next' % (endAge, phase['startAge']))
            return(False, errStr)
        else:
            endAge = phase['endAge']
    if finplan['AgeToday'] != phaseList[0]['startAge']:
        errStr = 'Age today (%d) is different from the starting age of the first Phase (%d)' % (finplan['AgeToday'], phaseList[0]['startAge'])
        return(False, errStr)
    if finplan['AgeEnd'] != phaseList[-1]['endAge']:
        errStr = ' End Age  (%d) is different from the end age of the last Phase (%d)' % (finplan['AgeEnd'] , phaseList[-1]['endAge'])        
        return(False, errStr)
    # Make sure that in each phase, the portfolio allocation adds up to 100% - If not, then adjust the cash - if cannot adjust the cash -> error
    assetList = HistoricalReturn.keys()  # List of asset types that we know about
    for phase in phaseList:
        totalPct = 0.0
        portfolio = phase['Portfolio']
        # print(portfolio)
        for asset, pct in portfolio.iteritems():  # compute sum of % of asset allocations for this phase
            totalPct += float(pct)
            if (asset not in assetList):  # Check that asset type is valid
                errStr = 'Unknown asset type %s in phase: %s' % (asset, phase['Name'])       
                return(False, errStr)                 
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
                return(False, errStr)   
    
    return (True,"it's all good")  # no errors

# ------------------
class FinPlanListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('FinPlan_ID', type = str, required = False,
           help = 'No plan ID provided', location = 'json')
        self.reqparse.add_argument('UserName', type = str, required = True,
           help = 'No plan UserName provided', location = 'json')
        self.reqparse.add_argument('Title', type = str, required = True,
           help = 'No Title  provided', location = 'json')
        self.reqparse.add_argument('Description', type = str, required = False,
           help = 'No plan Description  provided', location = 'json')
        self.reqparse.add_argument('Email', type = str, required = True,
           help = 'No Email  provided', location = 'json')
        self.reqparse.add_argument('HasResult', type = bool, required = False,
           help = 'No Result Flag  provided', location = 'json')
        self.reqparse.add_argument('AgeToday', type = float, required = False,
           help = 'No age provided', location = 'json')
        self.reqparse.add_argument('AgeEnd', type = float, required = False,
           help = 'No End age provided', location = 'json')
        self.reqparse.add_argument('StartingAmount', type = float, required = True,
           help = 'No Starting Investment amount provided', location = 'json')
        self.reqparse.add_argument('PhaseList', type = list, required = False,
            help = 'No Phases provided', location = 'json')
        self.reqparse.add_argument('InflationRate', type = float, required = False,
           help = 'No Inflation Rate provided', location = 'json')
                
        super(FinPlanListAPI, self).__init__()
    
    
    def get(self):
        return { 'Financial Plans': map(lambda plan: marshal(plan, finplan_fields), FinPlanScenario) }

    def post(self):
        args = self.reqparse.parse_args()
        finplan = {
            'FinPlan_ID': str(uuid.uuid4()),  # Generate a UUID - Don't understand why it needs to be cast to String - but does not work otherwise
            'Title': args['Title'],
            'UserName': args['UserName'],
            'Email': args['Email'],
            'StartingAmount': float(args['StartingAmount']),
            'HasResult': False  # force it False, even it is passed as argument
        }
        # Check if other values have been specified. If not, add the default values
        
        # ToDo: make sure to handle PhaseList argument
        
        for key, value in DefaultFinPlanValue.iteritems():
            # print ('Default: key: %s value: %s args: %s' % (key, value, args.get(key, value)))
            if args.get(key) == None: 
                finplan[key] = value
            else:
                finplan[key] = float(args[key])  # Note that new fields may require different casting
        # Validate the plan - exit if not OK
        planOK, errString = FinPlanIsOK(finplan)
        if (not planOK):
            print(errString)
            exit(-1)
        else: # plan is OK - add to the List
            FinPlanScenario.append(finplan)
        return { 'Financial Plan': marshal(finplan, finplan_fields) }, 201
    
# ------------------
class SinglePlanAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # None of the arguments are required when making updates
        self.reqparse.add_argument('FinPlan_ID', type = str, required = False,
           help = 'No plan ID provided', location = 'json')
        self.reqparse.add_argument('UserName', type = str, required = False,
           help = 'No plan UserName provided', location = 'json')
        self.reqparse.add_argument('Title', type = str, required = False,
           help = 'No Title  provided', location = 'json')
        self.reqparse.add_argument('Description', type = str, required = False,
           help = 'No Description  provided', location = 'json')
        self.reqparse.add_argument('Email', type = str, required = False,
           help = 'No Email  provided', location = 'json')
        self.reqparse.add_argument('HasResult', type = bool, required = False,
           help = 'No Result Flag  provided', location = 'json')
        self.reqparse.add_argument('AgeToday', type = float, required = False,
           help = 'No age provided', location = 'json')
        self.reqparse.add_argument('AgeEnd', type = float, required = False,
           help = 'No End age provided', location = 'json')
        self.reqparse.add_argument('StartingAmount', type = float, required = False,
           help = 'No Starting Inverstment amount provided', location = 'json')
        self.reqparse.add_argument('PhaseList', type = list, required = False,
            help = 'No Phases provided', location = 'json')
        self.reqparse.add_argument('InflationRate', type = float, required = False,
           help = 'No Inflation Rate provided', location = 'json')
        super(SinglePlanAPI, self).__init__()
         
    def get(self, plan_id):
        # FinPlanList = filter(lambda t: t['FinPlan_ID'] == id_string, FinPlanScenario)
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        return { 'Financial Plan': marshal(FinPlanList[0], finplan_fields) }
    
    def put(self, plan_id):
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        finplan = FinPlanList[0]
        args = self.reqparse.parse_args()
        for key, val in args.iteritems():
            if val != None:
                finplan[key] = val
        # Validate the plan - exit if not OK
        planOK, errString = FinPlanIsOK(finplan)
        if (not planOK):
            print(errString)
            exit(-1)
        return { 'Financial Plan': marshal(finplan, finplan_fields) }, 201
    
    def post(self, plan_id):
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        finplan = FinPlanList[0]
        args = self.reqparse.parse_args()
        # IGNORE all arguments other than "Run"
        if (args.get('Run', None) != True):
                print('POST Error - key = %s  value = %s' % (key, val))
                abort(500)        
        # RunScenario(finplan)
        finplan = MonteCarlo(finplan, DefaultMeanRate, DefaultStddevRate, DefaultNbRun, DefaultConfidenceFactor)
        
        return { 'Financial Plan': marshal(finplan, finplan_fields) }, 201         

    def delete(self, plan_id):
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        FinPlanScenario.remove(FinPlanList[0])
        return { 'result': True }
    
    
# ------------------
class ComputePlanAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # No arguments
        super(ComputePlanAPI, self).__init__()
         
    def get(self, plan_id):
        # FinPlanList = filter(lambda t: t['FinPlan_ID'] == id_string, FinPlanScenario)
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        # Compute the FinPlan passed as argument
        print ("Computing Plan w/ ID: %s" % FinPlanList[0]['FinPlan_ID'])
        # ToDo: Do the real computations
        return { 'Financial Plan': marshal(FinPlanList[0], finplan_fields) }                
            
api.add_resource(FinPlanListAPI, '/finplan/api/v1.0/finplan', endpoint = 'FinPlan')
api.add_resource(SinglePlanAPI, '/finplan/api/v1.0/finplan/<plan_id>', endpoint = 'SinglePlan')
api.add_resource(ComputePlanAPI, '/finplan/api/v1.0/finplan/<plan_id>/compute', endpoint = 'ComputePlan')

# ------------------------------------------------------

# Error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.errorhandler(400)
def missing_param(error):
    return make_response(jsonify( { 'error': 'FinPlan Create requires Title, Description, Email' } ), 401)


# ------------------
if __name__ == '__main__':
    app.run(debug = True)
    