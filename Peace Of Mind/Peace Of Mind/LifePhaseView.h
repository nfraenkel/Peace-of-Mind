//
//  LifePhaseView.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/11/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

@protocol LifePhaseViewDelegate <NSObject>

-(void)phaseWithNumberShouldBeDeleted:(int)number;

@end

@interface LifePhaseView : UIView

@property (nonatomic, readwrite) int phaseNumber;

@property (strong, nonatomic) id<LifePhaseViewDelegate> delegate;

@property (strong, nonatomic) IBOutlet UIView *contentView;

@property (weak, nonatomic) IBOutlet UIButton *deleteButton;

@property (weak, nonatomic) IBOutlet UITextField *nameTextField;
@property (weak, nonatomic) IBOutlet UILabel *phaseNumberLabel;
@property (weak, nonatomic) IBOutlet UITextField *startAgeTextField;
@property (weak, nonatomic) IBOutlet UITextField *endAgeTextField;
@property (weak, nonatomic) IBOutlet UITextField *bondPercentageTextField;
@property (weak, nonatomic) IBOutlet UITextField *cashPercentageTextField;
@property (weak, nonatomic) IBOutlet UITextField *stocksPercentageTextField;
@property (weak, nonatomic) IBOutlet UITextField *tBillsPercentageTextField;

//-(id)initWithFrame:(CGRect)frame;
-(void)awakeFromNib;
-(IBAction)deleteButtonTouched:(id)sender;

@end
