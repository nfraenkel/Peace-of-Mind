var request = require('superagent');

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
			console.log('Description: ' + fplan.Description)
			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};

exports.updateByID = function (fp, fn) {
	var finplanID = fp.FinPlan_ID;
	// console.log(fp)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log('updatebyID: finplanID: '+ finplanID +  "url:" + url)
	request.put(url)
    .type('json')
    .accept('json')
	.send(fp)
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			// console.log ("updateByID: res.error")
			// console.log (res.error)
			// console.log ("updateByID: res.status")
			// console.log (res.status)
			// console.log ("updateByID: res.text")
			// console.log (res.text)
			var fplan = res.body['Financial Plan']
			// console.log(fplan)
			console.log('Description: ' + fplan.Description)
			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};