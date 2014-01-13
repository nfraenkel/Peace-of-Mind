#!/usr/local/bin/python

'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
http://flask.pocoo.org/docs/quickstart/
http://flask-restful.readthedocs.org/en/latest/

Tests the passing of scenarios via HTTP REST API - to make sure that the Json structures are correct

NOTE: for the time being, the PhaseList has to be passed monolithically in the PUT command. This is the only way to allow editing or deleting a phase
Computes the amount of $$ that can be withdrawn during retirement - using Monte-Carlo simulations
All inputs are within the program
A scenario includes a number of phases (e.g. working, semi-retirement, retirement)
Each phase has a portfolio allocation of asset types (stocks, bonds, etc), and a contribution (negative for withdrawal). 
If the "ToCompute" flag is set in a phase, then the contribution (in this case withdrawal) will be computed by the MC simulations.
More that one phase can set ToCompute, but all these phases will share the same value in NetContribution
The MC simulations use the Historical mean,stddev for each asset class - and generate random rate of returns using a normal distribution based on the mean/stddev of the given asset class
The simulations are run "NbRun" and the contribution amount is returned based on the confidence factor 

01/12/2014 - added ability to read from and store data to file. The filename is name_of_program.data
'''

import finplan_lib as FP
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, \
    marshal_with
from getopt import GetoptError, gnu_getopt as getopt
import json
import os
import string
import sys
import uuid

app = Flask(__name__)
api = Api(app)


# ToDo: Replace the following default values by arguments - or config variables
# Default Values
DefaultNbRun = 10000
DefaultConfidencePct = 85 # % between 0-100
ConfigParam = dict()  # so that we can set the command line arguments & pass them globally
DefaultLifeExpect = 90
DefaultInflationRate = 2.0
DefaultEndFunds = 1.0 # Default value for target end funds at end of retirement
DefaultDebug = False
USAGE = '-c confidence_percentage -r run_count_for_monte_carlo -N -D'

# Global variable
FinPlanScenario = dict()

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
# ** Make sure that the required and DEFAULT attributes are all there (not necessarily w/ default values)
# Declare it in a single dict - this way, we only have to maintain it here - the rest of the code should just iterate the dict
DefaultFinPlanValue = {
    'LifeExpect': DefaultLifeExpect,
    'InflationRate': DefaultInflationRate,
    'TargetEndFunds': DefaultEndFunds
}

# Pre-loading w/ a couple of scenarios - whose IDs will be the same after server restart
DefaultFinPlanScenario = [
    {
        'FinPlan_ID': '445585fb-5c9d-4254-9b91-0197a584e6ba',
        'UserName': 'Lucky',
        'Title': 'Conservative',
        'Description': 'Conservative Scenario', 
        'Email': 'SantaClaus@xmas.com',
        'HasResult': False,
        'AgeToday': 30, 
        'LifeExpect': 90,
        'StartingAmount': 200000,
        'TargetEndFunds': 1.0,
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
        'LifeExpect': 90,
        'StartingAmount': 200000,
        'TargetEndFunds': 1000,
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
    'LifeExpect': fields.Float,
    'StartingAmount': fields.Float,
    'TargetEndFunds': fields.Float,
    'PhaseList': fields.List(fields.Nested(phase_fields)),
    'InflationRate': fields.Float    
}

# ------------------
def handleArgs(argv):
    '''
    handle command line arguments:
    '''

    Usage = ('Usage error - Syntax is: %s: %s' % (sys.argv[0], USAGE))
    try:
        opts, args = getopt(argv, 'c:r:ND', ['confidence=', 'runcount=', 'NewFile' 'Debug'])
    except GetoptError as e:
        print(e)
        print(Usage)
        sys.exit(2)

    # set default values for arguments
    Args = dict()
    Args['ConfidencePct'] = DefaultConfidencePct
    Args['NbRun'] = DefaultNbRun
    Args['NewFile'] = False
    Args['Debug'] = False

     # Read arguments from command line
    for opt, arg in opts:
        if opt in ('-c', '--confidence'):
            Args['ConfidencePct'] = int(arg)
            if Args['ConfidencePct'] < 0 or Args['ConfidencePct'] >100:
                print(Usage)
                print('Confidence is a % value between 0 and 100')
                exit (-3)
        elif opt in ('-r', '--runcount'):
            Args['NbRun'] = int(arg)
            if Args['NbRun'] <=0:
                print(Usage)
                print('The number of runs must be positive')
                exit (-3)
        elif opt in ('-N', '--NewFile'):
            Args['NewFile'] = True
        elif opt in ('-D', '--Debug'):
            Args['Debug'] = True
    # Done parsing command line

    # Verify we have the required arguments  -> N/A here

    if (Args['Debug']):  # Debug is true - print all the arguments we read
        for key in Args.keys():
            print('Arg %s= %s' % (key, Args[key]))

    return (Args)

# ------------------
def persist(fileName, jsonObject):
    with open(fileName, 'w') as outFile:
        json.dump(jsonObject, outFile, sort_keys = True, indent = 4, ensure_ascii=False)
        
    return    
    
# ------------------
def makeBaseName(argv, ExtensionString):
    
    '''
    Create a file name based on the program name and the extension provided as argument
    program name = /usr/me/mylib/Example.py   ExtensionString: ".data"
    filename: ./Example.data
    Note that the file points to the current local directory (and not where the program is stored)
    '''

    # Create the name for files
    # returns string ProgName-Date
    # ProgName is the base name of the calling program - without the '.py'
    # Date is today's date: YYYY-MM-DD
    fileBaseName = os.path.basename(sys.argv[0])
    strLen = len(fileBaseName)
    extension = fileBaseName[strLen - 3:strLen]
    if (extension == '.py'):
        fileBaseName = fileBaseName[0:strLen - 3]
    outDir = '.'
    fileBaseName = ('%s/%s%s' % (outDir, fileBaseName, ExtensionString))  # Store them in the current local directory

    return(fileBaseName)
# ------------------
def FinPlanIsOK(finplan):
    '''
    Validates that the finplan passed as argument is OK syntactically
    Returns 2 arguments: Flag + ErrorString. Flag is True if the plan is OK (in which case Error String can be ignored)
    
    ToDo: Make 2 versions: one "soft" - that does not assume everything is complete - one "hard" - that makes sure the plan is ready to be computed
    '''
    
    # ToDo: Perform validation of the fields other than those in PhaseList:  e.g. All required fields present, Age >=0 Inflation rate >= 0.0
    if finplan.get('LifeExpect', None) == None:
        finplan['LifeExpect'] = DefaultLifeExpect
    if finplan['AgeToday'] >= finplan['LifeExpect']:
        return (False,"End Age needs to be greater than age Today")
    
    if (finplan.get('PhaseList') == None):
        return (True,"it's all good - but needs the Phases")  # no errors

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
    if finplan['LifeExpect'] != phaseList[-1]['endAge']:
        errStr = ' End Age  (%d) is different from the end age of the last Phase (%d)' % (finplan['LifeExpect'] , phaseList[-1]['endAge'])        
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
        self.reqparse.add_argument('AgeToday', type = float, required = True,
           help = 'No age provided', location = 'json')
        self.reqparse.add_argument('LifeExpect', type = float, required = False,
           help = 'No End age provided', location = 'json')
        self.reqparse.add_argument('StartingAmount', type = float, required = True,
           help = 'No Starting Investment amount provided', location = 'json')
        self.reqparse.add_argument('TargetEndFunds', type = float, required = False,
           help = 'No Target End Funds amount provided', location = 'json')
        self.reqparse.add_argument('PhaseList', type = list, required = False,
            help = 'No Phases provided', location = 'json')
        self.reqparse.add_argument('InflationRate', type = float, required = False,
           help = 'No Inflation Rate provided', location = 'json')
                
        super(FinPlanListAPI, self).__init__()
    
    
    def get(self):
        print('GET')
        print(json.dumps(FinPlanScenario, sort_keys = True, indent = 4))
        print('DefaultFinPlanScenario')
        print(json.dumps(DefaultFinPlanScenario, sort_keys = True, indent = 4))        
        return { 'Financial Plans': map(lambda plan: marshal(plan, finplan_fields), FinPlanScenario) }

    def post(self):
        # ToDo: Capture the Optional arguments (e.g. Description) that are passed as arguments
        args = self.reqparse.parse_args()
        finplan = {
            'FinPlan_ID': str(uuid.uuid4()),  # Generate a UUID - Don't understand why it needs to be cast to String - but does not work otherwise
            'Title': args['Title'],
            'UserName': args['UserName'],
            'Email': args['Email'],
            'AgeToday': float(args['AgeToday']),
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
            persist(jsonFileName, FinPlanScenario)

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
        self.reqparse.add_argument('LifeExpect', type = float, required = False,
           help = 'No End age provided', location = 'json')
        self.reqparse.add_argument('StartingAmount', type = float, required = False,
           help = 'No Starting Investment amount provided', location = 'json')
        self.reqparse.add_argument('TargetEndFunds', type = float, required = False,
           help = 'No Target End Funds amount provided', location = 'json')
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
        persist(jsonFileName, FinPlanScenario)        
        return { 'Financial Plan': marshal(finplan, finplan_fields) }, 201
    
    def delete(self, plan_id):
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        FinPlanScenario.remove(FinPlanList[0])
        persist(jsonFileName, FinPlanScenario)
        return { 'result': True }
      
# ------------------
class ComputePlanAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # No arguments
        super(ComputePlanAPI, self).__init__()
      
    # This is where the action is - and the withdrawal amount for the given FinPlan is computed 
    def get(self, plan_id):
        # FinPlanList = filter(lambda t: t['FinPlan_ID'] == id_string, FinPlanScenario)
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        if len(FinPlanList) == 0:
            abort(404)
        else:
            finplan = FinPlanList[0]
        # Compute the FinPlan passed as argument
        ConfidencePct = ConfigParam['ConfidencePct']
        NbRun = ConfigParam['NbRun']
        print ("Computing Plan w/ ID: %s - with %d Runs & Confidence %%: %d" % (finplan['FinPlan_ID'],NbRun, ConfidencePct))
        # Do the real computations
        okFlag, errorString = FinPlanIsOK(finplan)
        if not okFlag:
            print(errorString)
            exit (-2)  # return an error response
        FP.MonteCarlo(finplan, NbRun, ConfidencePct, HistoricalReturn)  # only 1 run to test
        print json.dumps(finplan, sort_keys=True, indent=4)          
        persist(jsonFileName, FinPlanScenario)
        
        return { 'Financial Plan': marshal(finplan, finplan_fields) }                
            
# ------------------
api.add_resource(FinPlanListAPI, '/finplan/api/v2.0/finplan', endpoint = 'FinPlan')
api.add_resource(SinglePlanAPI, '/finplan/api/v2.0/finplan/<plan_id>', endpoint = 'SinglePlan')
api.add_resource(ComputePlanAPI, '/finplan/api/v2.0/finplan/<plan_id>/compute', endpoint = 'ComputePlan')

# ------------------------------------------------------

# Error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.errorhandler(400)
def missing_param(error):
    return make_response(jsonify( { 'error': 'FinPlan Create requires Title, Description, Email' } ), 401)


# ------------------
def main(argv):
    
    global FinPlanScenario
    global jsonFileName
    
    # Load arguments:
    Args = handleArgs(argv)
    Debug = Args['Debug']
    ConfigParam['ConfidencePct'] = Args['ConfidencePct']
    ConfigParam['NbRun'] = Args['NbRun']
    NewFileFlag = Args['NewFile']
    print ('NbRun %d Confidence Pct: %d' % (ConfigParam['NbRun'], ConfigParam['ConfidencePct']))
    jsonFileName = makeBaseName(argv, '.data') 
    print ('Storage file is: %s' % jsonFileName)
    
    # Run the REST API server'
    if (not NewFileFlag): # Load FinPlanScenario w/ the data from file
        try:
            inFile = open (jsonFileName, 'r')
            FinPlanScenario = json.load(inFile)
            inFile.close()
        except IOError, e:
            print("IOError %d: %s" % (e.args[0], e.args[1]))
            print ('error reading the data file: %s' % jsonFileName)
            FinPlanScenario = DefaultFinPlanScenario
            print('Starting w/ the default FinPlanScenario')
    else:
        FinPlanScenario = DefaultFinPlanScenario
        print('Starting w/ the default FinPlanScenario')
    print(json.dumps(FinPlanScenario, sort_keys = True, indent = 4))
    
    # Write the scenarios to file
    persist(jsonFileName, FinPlanScenario)
    
    # Run the REST API server
    app.run(debug = True)
    
    exit
    
# ------------------
if __name__ == '__main__':
    main(sys.argv[1:])    
    