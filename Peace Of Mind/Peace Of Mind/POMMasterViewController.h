//
//  POMMasterViewController.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "POMSingleton.h"

#import "GetScenariosCommand.h"

#import "Scenario.h"

@interface POMMasterViewController : UITableViewController <GetScenariosDelegate>

@property (strong) POMSingleton *singleton;

@end
