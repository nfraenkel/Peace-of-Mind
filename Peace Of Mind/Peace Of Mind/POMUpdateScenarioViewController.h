//
//  POMUpdateScenarioViewController.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "LifePhaseView.h"

@interface POMUpdateScenarioViewController : UIViewController <UIScrollViewDelegate, LifePhaseViewDelegate> {
    int nextPhaseListViewCoordinate;
    int nextPhaseNumber;
    NSMutableArray *phaseViewArray;
}

@property (weak, nonatomic) IBOutlet UIScrollView *scrolley;
@property (weak, nonatomic) IBOutlet UIView *backgroundView;
@property (weak, nonatomic) IBOutlet LifePhaseView *firstLifePhaseView;

@property (weak, nonatomic) IBOutlet UIButton *computeButton;
@property (weak, nonatomic) IBOutlet UIProgressView *computationProgressView;

- (IBAction)closeButtonTouched:(id)sender;
- (IBAction)saveButtonTouched:(id)sender;
- (IBAction)addPhaseButtonTouched:(id)sender;
- (IBAction)computeButtonTouched:(id)sender;

@end
