#!flask/bin/python
'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
http://flask.pocoo.org/docs/quickstart/
http://flask-restful.readthedocs.org/en/latest/

V1.2 replaces the iterative withdrawal computation with a straight calculation, since the relationship Return Rate -> Withdrawal is linear
'''

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.views import MethodView
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
import uuid
import locale
import math
import string

app = Flask(__name__)
api = Api(app)

# Default Values
DefaultEndFunds = 1.0 # Default value for target end funds at end of retirement
InitialStep = 50000 # starting increment
StepEpsilon = 0.5  # Multiplicative step adjustment
FinalDelta = 1.0  # stop incrementing when delta with TargetEndFunds is smaller than this


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
        'PreContribution': 17500,
        'PreReturnRate': 5.0,
        'RetirementReturnRate': 4.0,
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
        'PreContribution': 27500,
        'PreReturnRate': 8.0,
        'RetirementReturnRate': 6.0,
        'InflationRate': 2.0        
    }
]

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
    'PreContribution': fields.Float,
    'PreReturnRate': fields.Float,
    'RetirementReturnRate': fields.Float,
    'InflationRate': fields.Float,
    'Withdrawal':fields.Float 
}
# ------------------
def same_sign (a,b):
    '''
    Returns True if the 2 arguments have the same sign, False otherwise
    '''
    if math.copysign(1,a) == math.copysign(1,b):
        return True
    else:
        return False

# ------------------
def run_1_year(StartFunds, return_rate, withdrawal):
    '''
    Compute funds at end of year based on:
    - starting funds
    - interest rate
    - withdrawal taken at START of year
    '''
    EndFunds = (1.0 + return_rate) * (StartFunds - withdrawal)
    return (EndFunds)

# ------------------
def run_all_years(WithdrawalAmount, finPlan):
    
    StartFunds = finPlan['StartingAmount']
    inflationRate = float(finPlan['InflationRate']) * 0.01
    NbYears = finPlan['AgeEnd'] - finPlan['AgeToday']
    withdrawalStart = finPlan['AgeRetirement'] - finPlan['AgeToday']
    inflationWithdrawal = WithdrawalAmount  # Increase withdrawal by inflation amount
    preReturnRate = float(finPlan['PreReturnRate']) * 0.01
    retirementReturnRate = float(finPlan['RetirementReturnRate']) * 0.01
    for yr in range(0,NbYears):
        inflationWithdrawal *= (1+inflationRate)
        if (yr < withdrawalStart):  # Before retirement
            withdrawal = - finPlan['PreContribution']  # Positive contribution == negative withdrawal
            EndFunds = run_1_year(StartFunds, preReturnRate, withdrawal)
        else: # During retirement
            withdrawal = inflationWithdrawal
            EndFunds = run_1_year(StartFunds, retirementReturnRate, withdrawal)
            
        s_f = locale.format("%d", int(StartFunds), grouping=True)
        e_f = locale.format("%d", int(EndFunds), grouping=True)
        # print ('Year: %d: start = $%s - end = $%s - withdrawal = $%.2f' % (yr,s_f, e_f, withdrawal))
        StartFunds = EndFunds
            
    return(EndFunds)

# ------------------
def compute_withdrawal(targetEndValue, finPlan):    
    '''
    For a given interest rate, find the withdrawal amount so that the EndFunds are equal to the targetEndValue
    In other words, what withdrawals can we afford based on interest rate?
    Version 2: the relationship between EndFunds and withdrawal is linear => compute Endfunds for 2 values and interpolate to get the results
    '''
    withdrawal_1 = 0
    withdrawal_2 = 100000
        
    EndFunds_1 = run_all_years(withdrawal_1, finPlan)
    EndFunds_2 = run_all_years(withdrawal_2, finPlan)
    A_Cst = (EndFunds_2 - EndFunds_1) / (withdrawal_2 - withdrawal_1)
    B_Cst = EndFunds_1 - A_Cst * withdrawal_1
    withdrawal = (targetEndValue - B_Cst) / A_Cst
    lastEndFunds = run_all_years(withdrawal, finPlan)
    
    return (withdrawal, lastEndFunds)
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
            'FinPlan_ID': str(uuid.uuid4()),  # Generate a UUID - Don't understand why it needs to be cast to String - but does not work otherwise
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
        print ('#FinPlanScenario =%d #FinPlanList = %d' % (len(FinPlanScenario), len(FinPlanList)))
        for plan in FinPlanScenario:
            print(plan['FinPlan_ID'])
        if len(FinPlanList) == 0:
            abort(404)
        return { 'Financial Plan': marshal(FinPlanList[0], finplan_fields) }
    def put(self, plan_id):
        FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
        for plan in FinPlanScenario:
            print(plan['FinPlan_ID'])
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
        RunScenario(finplan)
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
