//
//  POMUpdateScenarioViewController.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "POMUpdateScenarioViewController.h"

#define SPACE_BETWEEN_PHASE_VIEWS   15
#define DEFAULT_CONTENT_HEIGHT      580

@interface POMUpdateScenarioViewController ()

@end

@implementation POMUpdateScenarioViewController

@synthesize scrolley, backgroundView, lifePhasesTableView, computeButton, computationProgressView, scenario;
@synthesize ageTodayTextField, descriptionTextField, inflationRateTextField, targetEndFundsTextField, startingAmountTextField, titleTextField, lifeExpectancyTextField;

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
    
    // set up scrolley
    scrolley.delegate = self;
    UITapGestureRecognizer *singleTap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(singleTapGestureCaptured:)];
    [scrolley addGestureRecognizer:singleTap];
    
    nextPhaseNumber = 2;
    
    // if we have an existing scenario, we CLONED!
    if (scenario) {
        titleTextField.text = scenario.title;
    }
}

-(void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    
    [scrolley setContentSize:CGSizeMake(0, DEFAULT_CONTENT_HEIGHT)];
}

#pragma mark - UITableViewDataSource methods
-(NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

-(NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return 2;
}

-(UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    NSString *phaseCellIdentifier = @"phaseCell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:phaseCellIdentifier forIndexPath:indexPath];
    
    return cell;
}

#pragma mark - UITableViewDelegate methods

#pragma mark - button handlers
- (IBAction)closeButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{}];
}

- (IBAction)saveButtonTouched:(id)sender {
    BOOL valid = [self isUserInputValid];
    if (valid) {
        [self dismissViewControllerAnimated:YES completion:^{}];
    }
}

- (IBAction)addPhaseButtonTouched:(id)sender {
    
    NSLog(@"ADDADDADDADDADD");
    
    // define frame for new phase view
    /*
    int x = self.firstLifePhaseView.frame.origin.x;
    int y = nextPhaseListViewCoordinate;
    CGRect newRectFrame = CGRectMake(x, y, 0, 0);
    // update helper variable!
    float updateSizeForViews    = firstLifePhaseView.frame.size.height + SPACE_BETWEEN_PHASE_VIEWS;
    nextPhaseListViewCoordinate += updateSizeForViews;
    
    // make new phase view
    LifePhaseView *newPhaseView = [[LifePhaseView alloc] initWithFrame:newRectFrame];
    [newPhaseView awakeFromNib];
    
    newPhaseView.delegate = self;
    [newPhaseView setUserInteractionEnabled:YES];
    [newPhaseView setAlpha:0.0f];
    [newPhaseView.deleteButton setHidden:NO];
    
    // add correct phase number
    newPhaseView.phaseNumber    = nextPhaseNumber++;
    
    // move compute button, computation progress bar
    CGRect oldComputeButtonFrame            = self.computeButton.frame;
    CGRect newComputeButtonFrame            = CGRectMake(oldComputeButtonFrame.origin.x, oldComputeButtonFrame.origin.y + updateSizeForViews, oldComputeButtonFrame.size.width, oldComputeButtonFrame.size.height);
    CGRect oldComputationProgessViewFrame   = self.computationProgressView.frame;
    CGRect newComputationProgressViewFrame  = CGRectMake(oldComputationProgessViewFrame.origin.x, oldComputationProgessViewFrame.origin.y + updateSizeForViews, oldComputationProgessViewFrame.size.width, oldComputationProgessViewFrame.size.height);
    
    // add to scrollview!
    [self.scrolley addSubview:newPhaseView];
    
    // add to phases array
    [phaseViewArray addObject:newPhaseView];
    
    // add animation
    [UIView animateWithDuration:0.5f animations:^{
        [newPhaseView setAlpha:1.0f];
        self.computeButton.frame            = newComputeButtonFrame;
        self.computationProgressView.frame  = newComputationProgressViewFrame;

    }];
    
    // update content size
    CGSize oldContentSize = scrolley.contentSize;
    self.scrolley.contentSize = CGSizeMake(oldContentSize.width, oldContentSize.height + updateSizeForViews);
     */
}

- (void)computeButtonTouched:(id)sender {

    NSLog(@"computing!!!...");
    
    BOOL valid = [self isUserInputValid];
    if (valid) {
        [self dismissViewControllerAnimated:YES completion:^{}];
    }
}

#pragma mark - helper methods
- (void)singleTapGestureCaptured:(UITapGestureRecognizer *)gesture {
    [self.view endEditing:YES];
}

-(void)createAlertViewWithTitle:(NSString*)title andMessage:(NSString*)message {
    UIAlertView *alert = [[UIAlertView alloc]
                          initWithTitle:title
                          message:message
                          delegate:Nil
                          cancelButtonTitle:@"OK"
                          otherButtonTitles:nil, nil];
    [alert show];
}

-(BOOL)isUserInputValid {
    BOOL userLeftSomethingBlank = [titleTextField.text isEqualToString:@""] || [descriptionTextField.text isEqualToString:@""] || [ageTodayTextField.text isEqualToString:@""] || [lifeExpectancyTextField.text isEqualToString:@""] || [startingAmountTextField.text isEqualToString:@""] || [targetEndFundsTextField.text isEqualToString:@""] || [inflationRateTextField.text isEqualToString:@""];
    if (userLeftSomethingBlank) {
        [self createAlertViewWithTitle:@"Fill Everything In" andMessage:@"You left something blank!"];
        return NO;
    }
    int ageToday        = [ageTodayTextField.text intValue];
    int lifeExpectancy  = [lifeExpectancyTextField.text intValue];
    BOOL agesAreInvalid = ageToday <= 0 || lifeExpectancy <= 0;
    if (agesAreInvalid) {
        [self createAlertViewWithTitle:@"Invalid Ages" andMessage:@"The ages you have entered are invalid."];
        return NO;
    }
    BOOL lifeExpectancyIsSmallerThanTodaysAge = ageToday >= lifeExpectancy;
    if (lifeExpectancyIsSmallerThanTodaysAge) {
        [self createAlertViewWithTitle:@"Invalid Ages" andMessage:@"Your life expectancy has to be greater than your age today!"];
        return NO;
    }
    
    return YES;
}

#pragma mark - memory
- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}


@end
