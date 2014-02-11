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

	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log('retrieveByID: finplanID: '+ finplanID + '   url: ' + url)
	request.get(url)
	.send({id:finplanID})
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			var fplan = res.body['Financial Plan']
			// console.log(fplan)
			// console.log('Title: ' + fplan.Title)

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
	var lateCareerAge = 50 // Time at which IRS authorizes higher contribution to IRA
	var retiringAge = 65
	var earlyCareerPortfolio = {"Stocks":100, "Bonds":0, "T-Bills":0, "Cash":0}
	var lateCareerPortfolio = {"Stocks":80, "Bonds":20, "T-Bills":0, "Cash":0}
	var retiredPortfolio = {"Stocks":40, "Bonds":40, "T-Bills":20, "Cash":0}
	// Set the default values of the phases - will adjust as necessary
	var earlyCareerPhase = {"Name":"Working", "startAge":fp.AgeToday, "endAge":lateCareerAge, "NetContribution":17500, "ToCompute":false, 
		"Portfolio":earlyCareerPortfolio}
	var lateCareerPhase = {"Name":"Late Career", "startAge":lateCareerAge, "endAge":retiringAge, "NetContribution":23000, "ToCompute":false, 
		"Portfolio":earlyCareerPortfolio}
	var retiredPhase = {"Name":"Retired", "startAge":retiringAge, "endAge":fp.LifeExpect, "NetContribution":0, "ToCompute":true, 
		"Portfolio":retiredPortfolio}
	fp.PhaseList = []		

	if (fp.AgeToday <= lateCareerAge) {
		if (fp.LifeExpect < lateCareerAge) {
			// AT - LE - lCA
			earlyCareerPhase.endAge = fp.LifeExpect  // need to adjust the end age
			fp.PhaseList.push(earlyCareerPhase)
		} else {  // fp.LifeExpect >= lateCareerAge
			fp.PhaseList.push(earlyCareerPhase) // keep the defaults for Phase 1
			if (fp.LifeExpect < retiringAge) {
				// AT - lCA - LE - rA
				lateCareerPhase.endAge = fp.LifeExpect  // need to adjust the end age
				fp.PhaseList.push(lateCareerPhase)
			} else {   // fp.LifeExpect >= retiringAge  -> we have the 3 phases with default ages
				// AT - lCA - rA - LE
				fp.PhaseList.push(lateCareerPhase)  // keep the defaults
				fp.PhaseList.push(retiredPhase)  // keep the defaults
			}
		}
	} else {  // fp.AgeToday > lateCareerAge
		if (fp.AgeToday <= retiringAge) {  // we can add the 2nd phase
			lateCareerPhase.startAge = fp.AgeToday			
			if (fp.LifeExpect < retiringAge) {
				// lCA - aT - LE - rA
				lateCareerPhase.endAge = fp.LifeExpect  // need to adjust the end age
				fp.PhaseList.push(lateCareerPhase)
			} else {   // fp.LifeExpect >= retiringAge  -> we have the 3 phases with default ages
				// lCA - aT  - rA - LE
				fp.PhaseList.push(lateCareerPhase)  // keep the defaults for the endAge
				fp.PhaseList.push(retiredPhase)  // keep the defaults
			}
		} else {  // fp.AgeToday > retiringAge -> only 3rd phase
			// lCA - rA - aT - LE
			retiredPhase.startAge = fp.AgeToday
			fp.PhaseList.push(retiredPhase)
		}
	}

	return (fp)
}
