//
//  POMUpdateScenarioViewController.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "POMUpdateScenarioViewController.h"

@interface POMUpdateScenarioViewController ()

@end

@implementation POMUpdateScenarioViewController

@synthesize scrolley;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view.
    
    self.scrolley.delegate = self;
    
    [self.scrolley setContentSize:CGSizeMake(0, 1000)];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)closeButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{
        
    }];
}

- (IBAction)saveButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{
        
    }];
}
@end
