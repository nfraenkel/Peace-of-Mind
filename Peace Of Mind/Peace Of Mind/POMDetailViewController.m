//
//  POMDetailViewController.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "POMDetailViewController.h"

@interface POMDetailViewController ()
- (void)configureView;
@end

@implementation POMDetailViewController

@synthesize singleton;

#pragma mark - Managing the detail item

- (void)setScenario:(Scenario*)newDetailItem
{
    if (self.scenario != newDetailItem) {
        _scenario = newDetailItem;
        
        // Update the view.
        [self configureView];
    }
}

- (void)configureView
{
    // Update the user interface for the detail item.

}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    self.singleton = [POMSingleton sharedDataModel];
    
    [self configureView];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

@end
