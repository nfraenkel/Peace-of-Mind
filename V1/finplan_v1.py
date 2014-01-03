#!flask/bin/python
'''
http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
http://flask.pocoo.org/docs/quickstart/
'''

from flask import Flask, jsonify, abort, make_response, request
import uuid

app = Flask(__name__)

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


@app.route('/finplan/api/v1.0/finplan', methods = ['GET'])
def get_scenario():
    return jsonify( { 'Financial Plans': FinPlanScenario } )


@app.route('/finplan/api/v1.0/finplan/<plan_id>', methods = ['GET'])
def get_finplan(plan_id):
    FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
    if len(FinPlanList) == 0:
        abort(404)
    return jsonify( { 'Financial Plans': FinPlanList[0] } )



@app.route('/finplan/api/v1.0/finplan', methods = ['POST'])
def create_finplan():
    # Ensure that required parameters are there
    if not request.json or not 'Title' in request.json or not 'Description' in request.json or not 'Email' in request.json:
        abort(400)
    finplan = {
        'FinPlan_ID': uuid.uuid4(),  # Generate a UUID
        'Title': request.json['Title'],
        'Description': request.json.get('Description'),
        'Email': request.json.get('Email'),
        'HasResult': False
    }
    # Add the default values
    for key, value in DefaultFinPlanValue.iteritems():
        finplan[key] = value
    FinPlanScenario.append(finplan)
    return jsonify( { 'Financial Plan': finplan } ), 201

@app.route('/finplan/api/v1.0/finplan/<plan_id>', methods = ['PUT'])
def update_task(plan_id):
    # FinPlanList = filter(lambda t: t['FinPlan_ID'] == plan_id, FinPlanScenario)
    FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
    if len(FinPlanList) == 0:
        abort(404)
    if not request.json:
        abort(400)
    finplan = FinPlanList[0]
    for key, val in request.json.iteritems():
        # ToDo: Make sure that the attribute passed is a legit attribute - and the argument has the correct type?
        finplan[key] = val
    # Note: finplan is a reference to the item in the list - so the stored list is automatically updated
    return jsonify( { 'Financial Plan': finplan } )

@app.route('/finplan/api/v1.0/finplan/<plan_id>', methods = ['DELETE'])
def delete_finplan(plan_id):
    FinPlanList = [plan for plan in FinPlanScenario if plan['FinPlan_ID'] == plan_id]
    if len(FinPlanList) == 0:
        abort(404)
    FinPlanScenario.remove(FinPlanList[0])
    return jsonify( { 'result': True } )

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
