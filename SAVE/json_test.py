#!/usr/local/bin/python

'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
http://flask.pocoo.org/docs/quickstart/
http://flask-restful.readthedocs.org/en/latest/

Tests the passing of scenarios via HTTP REST API - to make sure that the Json structures are correct
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
}
# ------------------
class FinPlanListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('Title', type = str, required = True,
            help = 'No plan Title provided', location = 'json')
        self.reqparse.add_argument('Description', type = str, required = True,
            help = 'No plan Description provided', location = 'json')
        self.reqparse.add_argument('UserName', type = str, required = True,
            help = 'No plan UserName provided', location = 'json')
        self.reqparse.add_argument('Email', type = str, required = True,
            help = 'No Email provided', location = 'json')
        super(FinPlanListAPI, self).__init__()
    
    
    def get(self):
        return { 'Financial Plans': map(lambda plan: marshal(plan, finplan_fields), FinPlanScenario) }

    def post(self):
        args = self.reqparse.parse_args()
        finplan = {
            'FinPlan_ID': str(uuid.uuid4()),  # Generate a UUID and cast to String
            'Title': args['Title'],
            'Description': args['Description'],
            'UserName': args['UserName'],
            'Email': args['Email'],
            'HasResult': False
        }
        # Add the default values
        for key, value in DefaultFinPlanValue.iteritems():
            finplan[key] = value 
        FinPlanScenario.append(finplan)
        return { 'Financial Plan': marshal(finplan, finplan_fields) }, 201
    
# ------------------
class SinglePlanAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('Title', type = str, location = 'json')
        self.reqparse.add_argument('Description', type = str, location = 'json')
        self.reqparse.add_argument('Email', type = str, location = 'json')
        self.reqparse.add_argument('UserName', type = str, location = 'json')
        self.reqparse.add_argument('AgeToday', type = int, location = 'json')
        self.reqparse.add_argument('AgeRetirement', type = int, location = 'json')
        self.reqparse.add_argument('AgeEnd', type = int, location = 'json')
        self.reqparse.add_argument('StartingAmount', type = int, location = 'json')
        self.reqparse.add_argument('PreContribution', type = int, location = 'json')
        self.reqparse.add_argument('PreReturnRate', type = float, location = 'json')
        self.reqparse.add_argument('RetirementReturnRate', type = float, location = 'json')
        self.reqparse.add_argument('InflationRate', type = float, location = 'json')
        self.reqparse.add_argument('Run', type = bool, location = 'json')
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
        #  Remove the WithDrawal attribute & Set HasResult to False to show that computation needs to be run
        if finplan.get('Withdrawal', None) != None:
            del finplan['Withdrawal']
        finplan['HasResult'] = False
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
        len1 = len(FinPlanScenario)
        FinPlanScenario.remove(FinPlanList[0])
        len2 = len(FinPlanScenario)
        print ('len1 = %d -- len2 = %d' % (len1, len2))
        return { 'result': True }            
            
api.add_resource(FinPlanListAPI, '/finplan/api/v1.0/finplan', endpoint = 'FinPlan')
api.add_resource(SinglePlanAPI, '/finplan/api/v1.0/finplan/<plan_id>', endpoint = 'SinglePlan')

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
    