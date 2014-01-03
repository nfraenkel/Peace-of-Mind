#! /bin/bash

echo "--------- Get the ID of the first Plan - so that we can use it later --------- "
planID=`curl -i http://localhost:5000/finplan/api/v1.0/finplan | grep -m 1 FinPlan_ID | sed -e 's/            "FinPlan_ID": "//' -e 's/",//'`
echo "First plan ID is: $planID"
echo

echo "--------- Run the Financial Plan --------- "
curl -i -H "Content-Type: application/json" -X POST -d '{"Run":true}' http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo
echo "--------- Show the results after execution: CHECK  Withdrawal & HasResult --------- "
curl -i http://localhost:5000/finplan/api/v1.0/finplan/$planID
echo