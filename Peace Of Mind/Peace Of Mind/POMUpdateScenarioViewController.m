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

@synthesize scrolley, backgroundView, firstLifePhaseView, computeButton, computationProgressView;

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
    
    // set up current phase view and array
    self.firstLifePhaseView.delegate = self;
    [self.firstLifePhaseView setPhaseNumber:1];
    phaseViewArray = [[NSMutableArray alloc] init];
    [phaseViewArray addObject:firstLifePhaseView];
    
    // set up variables for next phase view
    nextPhaseListViewCoordinate = firstLifePhaseView.frame.origin.y + firstLifePhaseView.frame.size.height + SPACE_BETWEEN_PHASE_VIEWS;
    nextPhaseNumber = 2;
    
}

-(void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    
    [self.scrolley setContentSize:CGSizeMake(0, DEFAULT_CONTENT_HEIGHT)];
}

#pragma mark - LifePhaseViewDelegate methods
-(void)phaseWithNumberShouldBeDeleted:(int)number {
    int currentLastPhase = [phaseViewArray count];
    
//    LifePhaseView *pv = [phaseViewArray objectAtIndex:number];
//
//    if (number == currentLastPhase) {
//        [UIView animateWithDuration:0.5f animations:^{
//            [pv setAlpha:0.0f];
//        } completion:^(BOOL finished) {
//            [pv removeFromSuperview];
//        }];
//    }
//    else {
//        
//    }
//    [phaseViewArray removeObjectAtIndex:number];

}

#pragma mark - button handlers
- (IBAction)closeButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{}];
}

- (IBAction)saveButtonTouched:(id)sender {
    [self dismissViewControllerAnimated:YES completion:^{}];
}

- (IBAction)addPhaseButtonTouched:(id)sender {
    
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

//    self.computeButton.frame            = newComputeButtonFrame;
//    self.computationProgressView.frame  = newComputationProgressViewFrame;
    
    // add to scrollview!
    [scrolley addSubview:newPhaseView];
    
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
}

- (void)computeButtonTouched:(id)sender {

    NSLog(@"computing!!!...");
    
    [self dismissViewControllerAnimated:YES completion:^{}];
}

#pragma mark - memory
- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}


@end
