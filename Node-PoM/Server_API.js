var request = require('superagent')
  , server_API = require('./server_API');

/**
 * retrieve function
 *
 * @param (String) retrieve query
 * @param (Function) callback
 * @api public
 */


 exports.retrieve = function (query, fn) {
	console.log('retrieve')
	request.get('http://localhost:5000/finplan/api/v2.0/finplan')
	// .set('Content-Type', 'application/json')
	.send({q:query})
	.end(function (res) {
		console.log(res.body['Financial Plans'])
		if (res.body && Array.isArray(res.body['Financial Plans'])) {
			return fn(null, res.body['Financial Plans']);
		}
		fn(new Error('Bad server response'))
	});
};



exports.retrieveByID = function (query, fn) {
	var finplanID =''
	// GET and POST method store the id in a different place
	if (query.params.id) 	{finplanID = query.params.id}
	else if (query.body.id) 	{ finplanID = query.body.id}
	else {
		console.log("Error cannot get the Finplan_ID  -- query ->")
		console.log(query)
	}

	console.log('retrieveByID: finplanID: '+ finplanID)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log ('url: ' + url)
	request.get(url)
	.send({id:finplanID})
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			var fplan = res.body['Financial Plan']
			// console.log(fplan)
			console.log('Title: ' + fplan.Title)

			// Sort Phases in FinPlan by startAge
			if (fplan.PhaseList) {	
				fplan.PhaseList.sort(function(a,b) {return a.startAge-b.startAge})
			}
			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};

exports.updateByID = function (fp, fn) {
	var finplanID = fp.FinPlan_ID;

	// console.log(fp)

	// Sort Phases in FinPlan by startAge
	if (fp.PhaseList) {	
		fp.PhaseList.sort(function(a,b) {return a.startAge-b.startAge})
	}

	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log('updatebyID: finplanID: '+ finplanID +  "url:" + url)
	request.put(url)
    .type('json')
    .accept('json')
	.send(fp)
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			var fplan = res.body['Financial Plan']
			// console.log(fplan)
			console.log('Title: ' + fplan.Title)
			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};

exports.createNew = function (fp, fn) {
	// console.log(fp)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan'
	request.post(url)
    .type('json')
    .accept('json')
	.send(fp)
	.end(function (res) {
		// if (res.body && Array.isArray(fplan)) {
		if (res.ok) {
			console.log('yay got ' + JSON.stringify(res.body));
			console.log("createNew - response body")
			console.log(res.body)
			var fplan = res.body['Financial Plan']
			// console.log(fplan)
			console.log('Title: ' + fplan.Title)
	    } else {
			// console.log("createNew: there was an error")
			// console.log(err)
			console.log('Oh no! error ' + res.text);
			fn(new Error('Bad server response'))
		}
		if (!fplan.PhaseList) {  // add default phases
			fplan = addDefaultPhaseList(fplan)
			console.log("createNew: add default Phases - new fp ->")
			console.log(fplan)
		    server_API.updateByID(fplan, function(error, fpnew) {
		    // server_API.retrieveByID(req.params.id, function(error, fp) {
		      // console.log("updateByID done")
		      // var url = "/" + fpnew.FinPlan_ID
		      // console.log("Title: " + fpnew.Title + "  url: " + url)
		      // res.redirect(url)
				return fn(null, fpnew);		
    		});
		} else {
			return fn(null, fplan);		
		}
	});
};

exports.computePlan  = function (query, fn) {
	var finplanID =''
	// GET and POST method store the id in a different place
	if (query.params.id) 	{finplanID = query.params.id}
	else {
		console.log("Error cannot get the Finplan_ID  -- query ->")
		console.log(query)
	}

	console.log('computePlan: finplanID: '+ finplanID)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID + '/compute'
	console.log ('url: ' + url)
	request.get(url)
	.send({id:finplanID})
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			var fplan = res.body['Financial Plan']
			// console.log(fplan)
			console.log('computePlan: Title: ' + fplan.Title)

			// Sort Phases in FinPlan by startAge
			fplan.PhaseList.sort(function(a,b) {return a.startAge-b.startAge})

			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};

exports.deleteByID = function (query, fn) {
	var finplanID =''
	// GET and POST method store the id in a different place
	if (query.params.id) 	{finplanID = query.params.id}
	else {
		console.log("Error cannot get the Finplan_ID  -- query ->")
		console.log(query)
	}

	console.log('deleteByID: finplanID: '+ finplanID)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log ('url: ' + url)
	request.del(url)
	.send({id:finplanID})
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			return fn(null);
		}
		fn(new Error('DeleteByID: Bad server response'))
	});
};

addDefaultPhaseList = function (fp) {
	var retiringAge = 65
	var workingPortfolio = {"Stocks":80, "Bonds":20, "T-Bills":0, "Cash":0}
	var retiredPortfolio = {"Stocks":40, "Bonds":40, "T-Bills":20, "Cash":0}
	var workingPhase = {"Name":"Working", "startAge":fp.AgeToday, "endAge":retiringAge, "NetContribution":17500, "ToCompute":false, 
		"Portfolio":workingPortfolio}
	var retiredPhase = {"Name":"Retired", "startAge":retiringAge, "endAge":fp.LifeExpect, "NetContribution":0, "ToCompute":true, 
		"Portfolio":retiredPortfolio}
	fp.PhaseList = [workingPhase, retiredPhase]
	return (fp)
}
