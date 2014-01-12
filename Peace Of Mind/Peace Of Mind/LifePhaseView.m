//
//  LifePhaseView.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/11/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "LifePhaseView.h"

@implementation LifePhaseView

@synthesize contentView, nameTextField, phaseNumberLabel, startAgeTextField, endAgeTextField, bondPercentageTextField, cashPercentageTextField, stocksPercentageTextField, tBillsPercentageTextField;

-(void)awakeFromNib {

    [[NSBundle mainBundle] loadNibNamed:@"LifePhaseView" owner:self options:nil];
    [self addSubview: self.contentView];
}

-(void)setPhaseNumber:(int)phaseNumber {
    if (_phaseNumber != phaseNumber) {
        _phaseNumber = phaseNumber;
        self.phaseNumberLabel.text = [NSString stringWithFormat:@"Phase %d", self.phaseNumber];
    }
}

/*
// Only override drawRect: if you perform custom drawing.
// An empty implementation adversely affects performance during animation.
- (void)drawRect:(CGRect)rect
{
    // Drawing code
}
*/

@end