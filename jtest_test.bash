#! /bin/bash

# ------------ NOTES  -----------
# Use '\' line continuation as the last character on the line between arguments
# but do NOT use it inside a string 
# Example:
# curl -i -H "Content-Type: application/json" -X PUT \
# -d '{"PhaseList":[ 
#             {"Name": "1-phase", 
#             "startAge": 30}]}' \
# http://localhost:5000/finplan/api/v1.0/finplan/$planID
#
# Use true/false in json (rather than True/False from Python)
# ------------ -----  -----------

function get_plan_id {
	planID=`curl -i http://localhost:5000/finplan/api/v1.0/finplan | grep -m 1 FinPlan_ID | sed -e 's/            \"FinPlan_ID\": \"//' -e 's/\",//' -e 's/ //g'`
	}

echo "--------- Show the list of all FinPlans - Make sure the new one is there --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan
echo

echo "--------- Get the ID of the first Plan - so that we can use it later --------- "
get_plan_id

echo "--------- Get a known FinPlan --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo
echo "--------- Create a new FinPlan --------- "
curl -i  -H "Content-Type: application/json" -X POST -d '{"Title": "Moderate", "Description": "Very Moderate",  "AgeEnd": 95,  "StartingAmount":250000, "UserName": "Suerte", "Email":"SantaClaus@xmas.com"}' http://localhost:5000/finplan/api/v1.0/finplan
echo
echo "--------- Show the list of all FinPlans - Make sure the new one is there --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan
echo

echo
echo "--------- UPDATE the First FinPlan --------- "
curl -i -H "Content-Type: application/json" -X PUT -d '{"Title":"Somewhat Moderate", "InflationRate": 2.5}' http://localhost:5000/finplan/api/v1.0/finplan/$planID

echo "--------- Make sure the value in the Stored list was updated --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo
echo "--------- DELETE the First FinPlan --------- "
curl -i  -X DELETE http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo
echo "--------- Make the plan was deleted - should get an Error--------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo

echo "--------- Get a new valid PlanID - so that we can use it later --------- "
get_plan_id
echo "New plan ID is: $planID"
echo

echo "--------- UPDATE PhaseList --------- "
curl -i -H "Content-Type: application/json" -X PUT \
-d '{"PhaseList":[
	{"Name": "Phase 1", 
            "startAge": 30, 
            "endAge": 65, 
            "NetContribution": 15000, 
            "ToCompute": false, 
            "Portfolio": {"Stocks": 99.0, "Bonds": 1.0, "T-Bills": 0.0, "Cash": 0.0}},
    {"Name": "Phase 2", 
            "startAge": 65, 
            "endAge": 90, 
            "NetContribution": 0, 
            "ToCompute": true, 
            "Portfolio": {"Stocks": 80.0, "Bonds": 20.0, "T-Bills": 0.0, "Cash": 0.0}}]}' \
http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo "--------- Make sure the new PhaseList replaces the old one --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo

echo "--------- Run the computation on the FinPlan --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID/compute

echo "--------- Show the results after execution: CHECK  Withdrawal & HasResult --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo