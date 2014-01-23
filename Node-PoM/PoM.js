/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , user = require('./routes/user')
  , http = require('http')
  , path = require('path')
  , retrieve = require('./retrieve'); 

var app = express();

app.configure(function(){
  app.set('port', process.env.PORT || 3000);
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.set('view options', {layout: false});
  app.use(express.favicon());
  app.use(express.logger('dev'));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
  app.use(require('stylus').middleware(__dirname + '/public'));
  app.use(express.static(path.join(__dirname, 'public')));
});

app.configure('development', function(){
  app.use(express.errorHandler());
});

app.enable('jsonp callback');

console.log(app.set('views'));

//Routes

//index
app.get('/', function(req, res, next){
  console.log(req.query);
  retrieve(req.query.q, function (err, fp) {
    if (err) return next(err);
    res.render('index', {
          title: 'FinPlan',
          finplan:fp
      });
  });
});

app.listen(process.env.PORT || 3000);
