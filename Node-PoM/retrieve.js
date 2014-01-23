var request = require('superagent');

/**
 * retrieve function
 *
 * @param (String) retrieve query
 * @param (Function) callback
 * @api public
 */

module.exports = function retrieve (query, fn) {
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