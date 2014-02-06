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

// List of asset types
asset_types = ["Stocks", "Bonds", "T-Bills", "Cash"]
phase_labels= ["Name", "startAge", "endAge", "NetContribution"]
floatList = ["AgeToday", "LifeExpect", "StartingAmount", "TargetEndFunds", "InflationRate"]
phaseFloatList = ["startAge", "endAge", "NetContribution"]
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


// Display the "Add Phase" page for a FinPlan
app.get('/:id/add_phase', function(req, res) {
  server_API.retrieveByID(req, function(error, fp) {
  // server_API.retrieveByID(req.params.id, function(error, fp) {
    console.log(fp.Description)
    res.render('finplan_add_phase',
    { 
      title: "Add a Phase to this Plan",
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
  var phID

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
      if (! req.body.Name) { // make sure the new name of the phase is not null
        console.log("Edit Phase - ERROR - new Phase name is null")
        //ToDo: handle the error gracefully
      }
      // Need to be careful because the name of the phase may have been edited
      // Find the phase that we want to modify
      for (var i=0; i < fp["PhaseList"].length; i++) {
        if (fp.PhaseList[i]["Name"] == req.body["Phase"]) {
          console.log("modifying Finplan - phase: " + req.body.Phase)
          phID = i
          break;
        }
      }
      console.log("updating Phase with (old) name: " + fp.PhaseList[phID]["Name"] + " New Name: " + req.body["Name"])
      console.log(fp.PhaseList[phID])
      for (index in req.body) {
        x = index.replace('asset/', '') // strip the 'asset/' prefix
        if (x != index) { // index had the 'asset/' prefix - so x is the label for the portfolio
          fp.PhaseList[phID]["Portfolio"][x]=parseFloat(req.body[index])
        } else if ((x != "id") && x != 'Phase') {
          console.log (x + ": body: " + req.body[x] + " fp: " + fp.PhaseList[phID][x])
          if (x == "ToCompute" || x == "Name") {
            fp.PhaseList[phID][x] = req.body[x]
          } else {
            fp.PhaseList[phID][x] = parseFloat(req.body[x])
          }
        }
      }
    }

    console.log ("PoM - pre-ParseFloat: fp")
    console.log(fp)
    // Convert all the values that need to, to float
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

// Save a new phase to a FinPlan
app.post('/:id/add_phase', function(req, res) {
  console.log('/add_phase post  -> req.body')
  console.log(req.body)

  var finplan = {}
  var phase = {}
  phase.Portfolio={}

  server_API.retrieveByID(req, function(error, fp) {
    // ToDo: Error checking - e.g. make sure all values have been entered
    for (var i=0; i<phase_labels.length; i++) {
      var label = phase_labels[i]
      var found = false
      for (index in req.body) {
        if (index == label) {
          found = true
          break
        }
      }
      if (!found) {
        if (label == "ToCompute") phase["ToCompute"] = false 
        else {
          // User did not enter value - ToDo Properly handle the error
          console.log("add_phase: ERROR - Value for " + label + " is missing! Can't accept the new phase")
          }        
      }
    }
    // for (var i; i<phase_labels.length; i++) {
    //   if (req.body.indexOf(phase_labels[i]) < 0) {
    //     // User did not enter value - ToDo Properly handle the error
    //     console.log("add_phase: ERROR - Value for " + phase_labels[i] + " is missing! Can't accept the new phase")
    //   }
    // }
    console.log("Adding NEW Phase with name: "  + req.body["Name"])
    for (index in req.body) {
      x = index.replace('asset/', '') // strip the 'asset/' prefix
      if (x != index) { // index had the 'asset/' prefix - so x is the label for the portfolio
        if (!req.body[index]) { // User has not entered anything
          phase["Portfolio"][x]=0.0
        } else {
          phase["Portfolio"][x]=parseFloat(req.body[index])          
        }
      } else {
        console.log (x + ": body: " + req.body[x])
        if (x == "ToCompute" || x == "Name") {
          phase[x] = req.body[x]
        } else {
          phase[x] = parseFloat(req.body[x])
        }
      }
    }
    console.log("/add_phase -> new phase")
    console.log(phase)

    // Add the new phase to the Finplan
    fp.PhaseList.push(phase)

    // Pass the updated Finplan to server - retrieve it and display it in Edit view
    server_API.updateByID(fp, function(error, fpnew) {
    // server_API.retrieveByID(req.params.id, function(error, fp) {
      console.log("add_phase: updateByID done")
      var url = "/" + fpnew.FinPlan_ID + "/edit"
      console.log("add_phase: Description: " + fpnew.Description + "  url: " + url)
      res.redirect(url)
    });
  });
});

// ToDo: delete a phase
app.post('/:id/delete_phase', function(req, res) {
  console.log('/delete_phase post  -> req.body')
  console.log(req.body)
  var planID = req.body.planID
  var phase_to_del = req.body.phase_to_del
  console.log("finplan ID = " + planID + " Phase to delete: " + phase_to_del)

  server_API.retrieveByID(req, function(error, fp) {
    // ToDo: Error checking - e.g. make sure all values have been entered
    var found_it = false
    var newList=[]
    console.log ("delete_phase - PhaseList length BEFORE: " + fp.PhaseList.length)
    for (var i=0, outString=""; i<fp.PhaseList.length; i++) outString = outString + "; " + fp.PhaseList[i]["Name"]
    console.log(outString)
    for (var i=0; i<fp.PhaseList.length; i++) {
      if (fp.PhaseList[i]["Name"] == phase_to_del) { // found the phase to delete
        console.log("Deleting Phase with name: "  + phase_to_del)
        fp.PhaseList.splice(i,1)
        found_it = true
        break
      } 
    }
    if (!found_it) { // ToDo: Error handling
      console.log("delete_phase - ERROR - Could not delete phase with name: " + phase_to_del)
    } 
    console.log ("delete_phase - PhaseList length AFTER: " + fp.PhaseList.length )
    for (var i=0, outString=""; i<fp.PhaseList.length; i++) outString = outString + "; " + fp.PhaseList[i]["Name"]
    console.log(outString)


    // for (var i=0; i<fp.PhaseList.length; i++) {
    //   if (fp.PhaseList[i]["Name"] == phase_to_del) { // found the phase to delete
    //     console.log("Deleting Phase with name: "  + phase_to_del)
    //     found_it = true
    //   } else { // keep it
    //     new_size = newList.push(fp.PhaseList[i])
    //   }
    // }
    // if (!found_it) { // ToDo: Error handling
    //   console.log("delete_phase - ERROR - Could not delete phase with name: " + phase_to_del)
    // } else {
    //   fp.PhaseList = newList
    // }
    // console.log ("delete_phase - PhaseList length AFTER: " + fp.PhaseList.length + " newList size: " + newList.length)

    // Pass the updated Finplan to server - retrieve it and display it in Edit view
    server_API.updateByID(fp, function(error, fpnew) {
      var url = "/" + fpnew.FinPlan_ID + "/edit"
      console.log("delete_phase: Description: " + fpnew.Description + "  url: " + url)
      res.redirect(url)
    });
  });
});

app.post('/:id/delete', function(req, res) {
  console.log('DELETE FinPlan: ' + req.body.id)
  res.redirect('/')

});

app.listen(process.env.PORT || 3000);
