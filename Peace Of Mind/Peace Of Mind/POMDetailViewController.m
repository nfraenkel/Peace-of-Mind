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

@synthesize singleton, descriptionLabel, titleLabel;

#pragma mark - Managing the detail item
- (void)setScenario:(Scenario*)newDetailItem
{
    if (self.scenario != newDetailItem) {
        _scenario = newDetailItem;
        
        // Update the view.
        [self configureView];
    }
}

#pragma mark - view stuff
- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    self.singleton = [POMSingleton sharedDataModel];
    
    [self configureView];
}

- (void)configureView
{
    // Update the user interface for the detail item.
    titleLabel.text         = _scenario.title;
    descriptionLabel.text   = _scenario.description;
    
}

#pragma mark - button handlers
-(IBAction)cloneButtonTouched:(id)sender {
    [self performSegueWithIdentifier:@"cloneScenario" sender:self];
}

-(void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    if ([[segue identifier] isEqualToString:@"cloneScenario"]) {
        UINavigationController *nav = (UINavigationController*)segue.destinationViewController;
        POMUpdateScenarioViewController *up = (POMUpdateScenarioViewController*)[nav topViewController];
        up.scenario = _scenario;
    }
}

#pragma mark - memory
- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

@end
