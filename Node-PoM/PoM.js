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
  console.log('GET -> req.body')
  console.log(req.body)
  console.log('GET  -> req.params')
  console.log(req.params)
  console.log('GET  -> req.query')
  console.log(req.query)  // console.log(req);
  // console.log(req.params.id);
  server_API.retrieveByID(req, function(error, fp) {
  // server_API.retrieveByID(req.params.id, function(error, fp) {
    console.log('-- fp --')
    console.log(fp.Description)
    res.render('finplan_details',
    { 
      title: "Financial Plan",
      finplan: fp
    });
  });
});

app.get('/:id/edit', function(req, res) {
  console.log('GET -> req.body')
  console.log(req.body)
  console.log('GET  -> req.params')
  console.log(req.params)
  console.log('GET  -> req.query')
  console.log(req.query)  // console.log(req);
  // console.log(req.params.id);
  server_API.retrieveByID(req, function(error, fp) {
  // server_API.retrieveByID(req.params.id, function(error, fp) {
    console.log('-- fp --')
    console.log(fp.Description)
    res.render('finplan_edit',
    { 
      title: "Financial Plan",
      finplan: fp
    });
  });
});

//Edit a FinPlan
app.post('/:id/edit', function(req, res) {
  console.log('/edit post  -> req.body')
  console.log(req.body)
  console.log('/edit post  -> req.params')
  console.log(req.params)
  console.log('/edit post  -> req.query')
  console.log(req.query)
  var section = ""
  var phase_to_del = ""
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
  var finplan = {}

  server_API.retrieveByID(req, function(error, fp) {
    console.log("modifying Finplan - section: " + section)
    if (section == "general") {
      for (x in req.body) {
        if (x != "id")  {
          console.log (x + ": body: " + req.body[x] + " fp: " + fp[x])
          fp[x] = req.body[x]
        }
      } 
    } else if (section == "phase") {
      // Need to be careful because the name of the phase may have been edited
      // Find the phase that we want to modify
      for (var i=0; i < fp["PhaseList"].length; i++) {
        if (fp.PhaseList[i]["Name"] == req.body["Phase"]) {
          console.log("modifying Finplan - phase: " + req.body.Phase)
          phase = fp.PhaseList[i]
          break;
        }
      }
      console.log("updating Phase with (old) name: " + phase["Name"] + " New Name: " + req.body["Phase"])
      console.log(phase)
      phase.Name = req.body.Phase  // Update the name if it has been modified
      for (index in req.body) {
        x = index.replace('asset/', '') // strip the 'asset/' prefix
        if (x != index) { // index had the 'asset/' prefix - so x is the label for the portfolio
          fp.PhaseList[i]["Portfolio"][x]=parseFloat(req.body[index])
        } else if ((x != "id") && x != 'Phase' && x != "Name") {
          console.log (x + ": body: " + req.body[x] + " fp: " + phase[x])
          if (x == "ToCompute") {
            fp.PhaseList[i][x] = req.body[x]
          } else {
            fp.PhaseList[i][x] = parseFloat(req.body[x])
          }
        }
      }
    }

    // Convert all the values that need to, to float
    var floatList = ["AgeToday", "LifeExpect", "StartingAmount", "TargetEndFunds", "InflationRate"]
    var phaseFloatList = ["startAge", "endAge", "NetContribution"]
    var label = ""
    for (var i=0; i < floatList.length; i++) {
      label = floatList[i]
      console.log(label)
      fp[label] = parseFloat(fp[label])
    }
    for (var ph =0 ; ph < fp.PhaseList.length; ph++) {
      for (var j=0; j < phaseFloatList.length; j++) {
        label = phaseFloatList[j]
        console.log(label)
        fp.PhaseList[ph][label] = parseFloat(fp.PhaseList[ph][label])
      }
      for (var label in fp.PhaseList[ph].Portfolio) {
        console.log(label)
        fp.PhaseList[ph].Portfolio[label] = parseFloat(fp.PhaseList[ph].Portfolio[label])
      }
    }
    console.log ("PoM - post: fp")
    console.log(fp)
    // Pass the updated Finplan to server - retrieve it and display it
    server_API.updateByID(fp, function(error, fpnew) {
    // server_API.retrieveByID(req.params.id, function(error, fp) {
      console.log("updateByID done")
      var url = "/" + fpnew.FinPlan_ID
      console.log("Description: " + fpnew.Description + "  url: " + url)
      res.redirect(url)
    });
  });
});



app.post('/:id/delete_phase', function(req, res) {
  console.log('/delete_phase post  -> req.body')
  console.log(req.body)
  console.log("finplan ID = " + req.body.planID + " Phase: " + req.body.phase_to_del)


// We don't store the value yet - just display it back

  // res.render('finplan_details',
  //   { 
  //     title: "Financial Plan",
  //     finplan: fp
  //   });
  });

app.post('/:id/delete', function(req, res) {
  console.log('DELETE FinPlan: ' + req.body.id)
  res.redirect('/')

});


app.listen(process.env.PORT || 3000);
