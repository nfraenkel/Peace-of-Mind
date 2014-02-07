Peace-of-Mind
=============

Financial planner and simulator by the FRAENKEL BOYS

Python Packages Required
------------------------
* string
* sys
* uuid
* math
* json
* flask 
* numpy 

Release Notes
-------------
* Rel 1.4 - 2/6/2014
	- Added  page to add a phase finpland-add-phase.jade
	- Made "delete phase" work
	
* Rel 1.3 - 2/1/2014
	- Added a read-only "Details" page - from which a Finplan can be edited
	- finplan-details.jade is now the read only version
	- finplan-edit.jade is the editable page (what used to be finplan-details.jade)

* Rel 1.2 - 1/31/2014
	- Fixed up the jade format for "finplan_details.jade" (and associated code in "PoM.js") so that all the buttons work. Problem was discovered when trying to add  "Delete Phase" button. Net-net: each phase div needs to have its own form (using the phase's name as id)
	- Code is still not functional but at least the right parameters are getting to the server-side node code
	- Also fixed the parameter passing in RetrieveByID: GET and POST store parameters in params and body sections, so the code accommodates that

* Rel 1.1
	- First kinda-working release of the node code. Does not do anything, except showing the data in pages

Useful Links
------------
* [Nice Tutorial on Flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful)
* [Documentation/Quickstart on Flask](http://flask.pocoo.org/docs/quickstart/)
* [Documentation on Flask RESTful](http://flask-restful.readthedocs.org/en/latest/)
* Historical rates of return
- [Historical rates of return for asset classes](http://fc.standardandpoors.com/sites/client/generic/axa/axa4/Article.vm?topic=5991&siteContent=8088)
- [History of Asset Class Returns](http://personalfinance.byu.edu/?q=node/652) -- see bottom of page
- [Wealthfront Investment Methodology White Paper](https://www.wealthfront.com/whitepapers/investment-methodology) -- see Table 2: Asset class correlation assumptions
- [Historical and expected returns - The Bogleheads](http://www.bogleheads.org/wiki/Historical_and_expected_returns)
* Life Expectancy Calculators
- [Worldwide life expectancy by age & gender](http://www.worldlifeexpectancy.com/your-life-expectancy-by-age)
- [How long will I live (long form)?](http://gosset.wharton.upenn.edu/mortality/perl/CalcForm.html)
- [How long will I live (short form)?](http://gosset.wharton.upenn.edu/mortality/form.html) -- See source code snippet [HERE](http://www.flexibleretirementplanner.com/wp/documentation/source-code/)
* Commercial Products
- [The Flexible Retirement Planner](http://www.flexibleretirementplanner.com/wp/)

ToDo Validation
---------------
* Phase Name has to be non-null and unique  (big doodoo if Name is null)
* All ages have to be consistent
- Between 0 and 125
- endAge of one phase has to be equal to startAge of the next one
- startAge of the first phase has to be the startAge of the FinPlan - similarly for endAge
- Asset allocations have to add up to 100%
* Net Allocations can be positive as well as negative


