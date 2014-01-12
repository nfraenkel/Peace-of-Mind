//
//  POMUpdateScenarioViewController.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "POMUpdateScenarioViewController.h"

#define SPACE_BETWEEN_PHASE_VIEWS   15

@interface POMUpdateScenarioViewController ()

@end

@implementation POMUpdateScenarioViewController

@synthesize scrolley, backgroundView, firstLifePhaseView, computeButton, computationProgessView;

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
    
    nextPhaseListViewCoordinate = firstLifePhaseView.frame.origin.y + firstLifePhaseView.frame.size.height + SPACE_BETWEEN_PHASE_VIEWS;
    nextPhaseNumber = 2;
}

-(void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    
    [self.scrolley setContentSize:CGSizeMake(0, 568)];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - button handlers
- (IBAction)closeButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{}];
}

- (IBAction)saveButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{}];
}

- (IBAction)addPhaseButtonTouched:(id)sender {
    NSLog(@"make new phase!!! currently: %@", self.firstLifePhaseView.phaseNumberLabel.text);
    
    // define frame for new phase view
    int x = self.firstLifePhaseView.frame.origin.x;
    int y = nextPhaseListViewCoordinate;
    CGRect newRectFrame = CGRectMake(x, y, 0, 0);
    // update helper variable!
    float updateSizeForViews    = firstLifePhaseView.frame.size.height + SPACE_BETWEEN_PHASE_VIEWS;
    nextPhaseListViewCoordinate += updateSizeForViews;
    
    // make new phase view
    LifePhaseView *newPhaseView = [[LifePhaseView alloc] initWithFrame:newRectFrame];
    [newPhaseView awakeFromNib];
    // add correct phase number
    newPhaseView.phaseNumber    = nextPhaseNumber++;
    
    // move compute button, computation progress bar
    CGRect oldComputeButtonFrame            = self.computeButton.frame;
    NSLog(@"%@", NSStringFromCGRect(oldComputeButtonFrame));
    CGRect newComputeButtonFrame            = CGRectMake(oldComputeButtonFrame.origin.x, oldComputeButtonFrame.origin.y + updateSizeForViews, oldComputeButtonFrame.size.width, oldComputeButtonFrame.size.height);
    CGRect oldComputationProgessViewFrame   = self.computationProgessView.frame;
    CGRect newComputationProgressViewFrame  = CGRectMake(oldComputationProgessViewFrame.origin.x, oldComputationProgessViewFrame.origin.y + updateSizeForViews, oldComputationProgessViewFrame.size.width, oldComputationProgessViewFrame.size.height);
    NSLog(@"%@", NSStringFromCGRect(newComputeButtonFrame));

//    self.computeButton.frame             = newComputeButtonFrame;
    [self.computeButton setFrame:CGRectMake(100, 100, 100, 100)];
    
        NSLog(@"%@", NSStringFromCGRect(self.computeButton.frame));
    self.computationProgessView.frame    = newComputationProgressViewFrame;
    
    // add to scrollview!
    [self.backgroundView addSubview:newPhaseView];
    
    // update content size
    CGSize oldContentSize = scrolley.contentSize;
    self.scrolley.contentSize = CGSizeMake(oldContentSize.width, oldContentSize.height + updateSizeForViews);
}

- (IBAction)computeButtonTouched:(id)sender {

    NSLog(@"computing!!!...");
    
    [self dismissViewControllerAnimated:YES completion:^{}];
}


@end
