var request = require('superagent');

/**
 * retrieve function
 *
 * @param (String) retrieve query
 * @param (Function) callback
 * @api public
 */


module.exports = function retrieveByID (query, fn) {
	console.log('retrieveByID')
	console.log(query)
	// var finplanID = query.params.id;
	var url = 'http://localhost:5000/finplan/api/v2.0/finplan/' + query
	console.log ('url: ' + url)
	request.get(url)
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