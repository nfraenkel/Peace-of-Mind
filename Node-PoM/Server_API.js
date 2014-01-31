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
	console.log('retrieveByID')
	var finplanID =''
	// GET and POST method store the id in a different place
	if (query.params.id) 	{finplanID = query.params.id}
	else if (query.body.id) 	{ finplanID = query.body.id}
	else {
		console.log("Error cannot get the Finplan_ID  -- query ->")
		console.log(query)
	}


	// console.log(query)
	// console.log(query.query._id)
	// var finplanID = query.query._id;

	console.log('finplanID: '+ finplanID)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log ('url: ' + url)
	request.get(url)
	// request.get('http://localhost:5000/finplan/api/v2.0/finplan')
	// .set('Content-Type', 'application/json')
	.send({id:finplanID})
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			var fplan = res.body['Financial Plan']
			console.log(fplan)
			console.log('Description: ' + fplan.Description)
			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};

exports.updateByID = function (query, fn) {
	console.log('updateByID')
	console.log(query)
	var finplanID = query.query._id;
	console.log('finplanID: '+ finplanID)
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + finplanID
	console.log ('url: ' + url)
	request.put(url)
	// request.get('http://localhost:5000/finplan/api/v2.0/finplan')
	// .set('Content-Type', 'application/json')
	.send({q:query})
	.end(function (res) {

		// if (res.body && Array.isArray(fplan)) {
		if (res.body) {
			var fplan = res.body['Financial Plan']
			console.log(fplan)
			console.log('Description: ' + fplan.Description)
			return fn(null, fplan);
		}
		fn(new Error('Bad server response'))
	});
};