#! /bin/bash

echo "--------- Get the ID of the first Plan - so that we can use it later --------- "
planID=`curl -i http://localhost:5000/finplan/api/v1.0/finplan | grep -m 1 FinPlan_ID | sed -e 's/            "FinPlan_ID": "//' -e 's/",//'`
echo "First plan ID is: $planID"
echo

echo "--------- Get a known FinPlan --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo

echo
echo "--------- ERROR: Try to get a known FinPlan with a bad uuid --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/388774d0-fd92-468c-b2cf-49039ce5c6c
echo

echo
echo "--------- Create a new FinPlan --------- "
curl -i  -H "Content-Type: application/json" -X POST -d '{"Title": "Moderate", "Description":"Moderate Portfolio", "UserName": "Suerte", "Email":"SantaClaus@xmas.com"}' http://localhost:5000/finplan/api/v1.0/finplan
echo
echo "--------- Show the list of all FinPlans - Make sure the new one is there --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan
echo

echo
echo "--------- UPDATE the First FinPlan --------- "
curl -i -H "Content-Type: application/json" -X PUT -d '{"Title":"Somewhat Moderate", "InflationRate": 2.5, "PreReturnRate": 4.0}' http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo "--------- Make sure the value in the Stored list was updated --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo

echo
echo "--------- DELETE the First FinPlan --------- "
curl -i  -X DELETE http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo
echo "--------- Make the plan was deleted - should get an Error--------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo

echo "--------- Get a new valid PlanID - so that we can use it later --------- "
planID=`curl -i http://localhost:5000/finplan/api/v1.0/finplan | grep -m 1 FinPlan_ID | sed -e 's/            "FinPlan_ID": "//' -e 's/",//'`
echo "New plan ID is: $planID"
echo

echo "--------- Run the Financial Plan --------- "
curl -i -H "Content-Type: application/json" -X POST -d '{"Run":true}' http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo  "--------- Lower the PreReturnRate, Run the Financial Plan and see the difference --------- "
curl -i -H "Content-Type: application/json" -X PUT -d '{"PreReturnRate": 4.0}' http://localhost:5000/finplan/api/v1.0/finplan/$planID
curl -i -H "Content-Type: application/json" -X POST -d '{"Run":true}' http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo "--------- Show the results after execution: CHECK  Withdrawal & HasResult --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo