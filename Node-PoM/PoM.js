/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , user = require('./routes/user')
  , http = require('http')
  , path = require('path')
  , server_API = require('./server_API');

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
  // console.log(req);
  server_API.retrieve(req.query.q, function (err, fp) {
    if (err) return next(err);
    res.render('index', {
          title: 'FinPlan',
          finplan:fp
      });
  });
});

//Show the details for FinPlan
app.get('/:id', function(req, res) {
  console.log(req.params);
  // console.log(req.params.id);
  // retrieveByID(req, function(error, fp) {
  server_API.retrieveByID(req.params.id, function(error, fp) {
    console.log('-- fp --')
    console.log(fp.Description)
    res.render('finplan_details',
    { 
      title: "Financial Plan",
      finplan: fp
    });
  });
});

//Edit a FinPlan
app.post('/edit', function(req, res) {
  console.log('/edit post')
  var section = ""
  for (x in req.body) { // determine which section of the page was updated
    if (x == "Phase") {
      section = "phase";
      break;
    } else if (x == "UserName") {
      section = "settings";
      break;
    } else if (x == "Title") {
      section = "general";
      break;
    }
  }
  console.log("Section: " + section);
  // console.log(req.body);
  server_API.retrieveByID(req.body.id, function(error, fp) {
    if (section == "general") {
      for (x in req.body) {
        if ((x != "id") && (x != "_id")) {
          console.log (x + ": body: " + req.body[x] + " fp: " + fp[x])
          fp[x] = req.body[x]
        }
      } 
    } else if (section == "phase") {
      // Need to be careful because the name of the phase may have been edited
      for (var i=0; i < fp["PhaseList"].length; i++) {
        phase = fp.PhaseList[i]
        if (phase["Name"] == req.body["Phase"]) {
          console.log("updating Phase with (old) name: " + phase["Name"])
          console.log(phase)
          fp.PhaseList[i].Name = req.body.Phase  // Update the name if it has been modified
          for (index in req.body) {
            x = index.replace('asset/', '') // strip the 'asset/' prefix
            if (x != index) { // index had the 'asset/' prefix - so x is the label for the portfolio
              fp.PhaseList[i]["Portfolio"][x]=req.body[index]
            } else if ((x != "id") && (x != "_id") && x != 'Phase' && x != "Name") {
              console.log (x + ": body: " + req.body[x] + " fp: " + phase[x])
              fp.PhaseList[i][x] = req.body[x]
            }
          }
        } // else do nothing
      }
    }


// We don't store the value yet - just display it back

  res.render('finplan_details',
    { 
      title: "Financial Plan",
      finplan: fp
    });
  });
});



app.listen(process.env.PORT || 3000);
