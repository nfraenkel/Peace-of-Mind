//
//  POMUpdateScenarioViewController.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface POMUpdateScenarioViewController : UIViewController <UIScrollViewDelegate>

@property (weak, nonatomic) IBOutlet UIScrollView *scrolley;

- (IBAction)closeButtonTouched:(id)sender;
- (IBAction)saveButtonTouched:(id)sender;

@end
