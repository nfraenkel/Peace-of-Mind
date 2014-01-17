//
//  POMUpdateScenarioViewController.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "LifePhaseView.h"

#import "Scenario.h"

@interface POMUpdateScenarioViewController : UIViewController <UIScrollViewDelegate, UITableViewDataSource, UITableViewDelegate, UITextFieldDelegate> {
    int nextPhaseListViewCoordinate;
    int nextPhaseNumber;
    NSMutableArray *phaseViewArray;
}

@property (nonatomic, strong) Scenario *scenario;

@property (weak, nonatomic) IBOutlet UIScrollView *scrolley;
@property (weak, nonatomic) IBOutlet UIView *backgroundView;
@property (weak, nonatomic) IBOutlet UITableView *lifePhasesTableView;

@property (weak, nonatomic) IBOutlet UIButton *computeButton;
@property (weak, nonatomic) IBOutlet UIProgressView *computationProgressView;

- (IBAction)closeButtonTouched:(id)sender;
- (IBAction)saveButtonTouched:(id)sender;
- (IBAction)addPhaseButtonTouched:(id)sender;
- (IBAction)computeButtonTouched:(id)sender;

@property (weak, nonatomic) IBOutlet UITextField *ageTodayTextField, *descriptionTextField, *inflationRateTextField, *targetEndFundsTextField, *startingAmountTextField, *titleTextField, *lifeExpectancyTextField;

@end
