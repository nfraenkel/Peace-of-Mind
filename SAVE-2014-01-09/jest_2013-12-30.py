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

# Populate the Array of Financial Plans with Initial Values
# ** Make sure that the required and DEFAULT attributes are all there (not necessarily w/ default values 
''' 
# Version with List
FinPlanScenario = [
    {
        'FinPlan_ID': '1',
        'UserName': 'Lucky',
        'Phase' : [ 'phase1', 'phase2']
    },
    {
        'FinPlan_ID': '2',
        'UserName': 'Chance',
        'Phase' : [ 'suerte', 'Gluck']
    }
]

# With Nested Dict
FinPlanScenario = [
    {
        'FinPlan_ID': '1',
        'UserName': 'Lucky',
        'Phase' : {'str1' :'1st', 'str2': '2nd'}
    },
    {
        'FinPlan_ID': '2',
        'UserName': 'Chance',
        'Phase' : {'str1' :'3rd', 'str2': '4th'}
    }
]
'''
FinPlanScenario = [
    {
        'FinPlan_ID': '1',
        'UserName': 'Lucky',
        'Phase' : [{'str1' :'1st', 'str2': '2nd','Portfolio': {"Stocks": 50.0, "Bonds": 30.0, "T-Bills": 10.0, "Cash": 10.0}}, 
                   {'str1' :'1st', 'str2': '2nd','Portfolio': {"Stocks": 60.0, "Bonds": 0.0, "T-Bills": 20.0, "Cash": 10.0}}]
    },
    {
        'FinPlan_ID': '2',
        'UserName': 'Chance',
        'Phase' : [{'str1' :'1st', 'str2': '2nd','Portfolio': {"Stocks": 20.0, "Bonds": 60.0, "T-Bills": 10.0, "Cash": 10.0}}]
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
    'Phase': fields.List(fields.String)
}


simple_fields = {
    'str1' : fields.String,
    'str2' : fields.String,
    'Portfolio': fields.Nested(portfolio_fields)
}

finplan_fields2 = {
    'FinPlan_ID': fields.String,
    'UserName': fields.String,
    'Phase': fields.Nested(simple_fields)
}
finplan_fields3 = {
    'FinPlan_ID': fields.String,
    'UserName': fields.String,
    'Phase': fields.List(fields.Nested(simple_fields))
}

# ------------------
class FinPlanListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        print('FinPlanListAPI initializing ')
        self.reqparse.add_argument('FinPlan_ID', type = str, required = True,
           help = 'No plan ID provided', location = 'json')
        self.reqparse.add_argument('UserName', type = str, required = True,
           help = 'No plan UserName provided', location = 'json')
        self.reqparse.add_argument('Phase', type = dict, required = False,
            help = 'No Phases provided', location = 'json')
        print('FinPlanListAPI arguments added ')
        
        super(FinPlanListAPI, self).__init__()
    
    
    def get(self):
        print('FinPlanListAPI GET ')
        print(json.dumps(FinPlanScenario))
        XX = map(lambda plan: marshal(plan, finplan_fields3), FinPlanScenario)
        print(json.dumps(XX))

        return { 'Financial Plans': map(lambda plan: marshal(plan, finplan_fields3), FinPlanScenario) }

    def post(self):
        args = self.reqparse.parse_args()
        finplan = {
            'UserName': args['UserName'],
            'Phase': args['Phase']
        }
        FinPlanScenario.append(finplan)
        return { 'Financial Plan': marshal(finplan, finplan_fields) }, 201
    
# ------------------
class SinglePlanAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        print('SinglePlanAPI initializing ')
        self.reqparse.add_argument('FinPlan_ID', type = str, location = 'json')
        self.reqparse.add_argument('UserName', type = str, location = 'json')
        self.reqparse.add_argument('Phase', type = list, location = 'json')

        
        super(SinglePlanAPI, self).__init__()
         
    def get(self, plan_id):
        # FinPlanList = filter(lambda t: t['FinPlan_ID'] == id_string, FinPlanScenario)
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        print('FinPlanList', FinPlanList)
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
    