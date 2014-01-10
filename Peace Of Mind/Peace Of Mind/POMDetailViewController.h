//
//  POMDetailViewController.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "POMSingleton.h"

#import "Scenario.h"

@interface POMDetailViewController : UIViewController

@property (strong) POMSingleton *singleton;

@property (strong, nonatomic) Scenario *scenario;

@property (weak, nonatomic) IBOutlet UILabel *detailDescriptionLabel;
@end
