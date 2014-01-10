//
//  Phase.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/9/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "Phase.h"

@implementation Phase

@synthesize name;
@synthesize netContribution, bondsPercentage, cashPercentage, stocksPercentage, tBillsPercentage, endAge, startAge;
@synthesize toCompute;

-(id)initWithDictionary:(NSDictionary*)dict {
    self = [super init];
    if (self) {
        // custom init
        self.name = [dict objectForKey:kPhaseKeyName];
        self.netContribution = [[dict objectForKey:kPhaseKeyNetContribution] doubleValue];
        
        NSDictionary *portfolio = [dict objectForKey:kPhaseKeyPortfolio];
        self.bondsPercentage = [[portfolio objectForKey:kPhaseKeyPortfolioBonds] doubleValue];
        self.cashPercentage = [[portfolio objectForKey:kPhaseKeyPortfolioCash] doubleValue];
        self.stocksPercentage = [[portfolio objectForKey:kPhaseKeyPortfolioStocks] doubleValue];
        self.tBillsPercentage = [[portfolio objectForKey:kPhaseKeyPortfolioTBills] doubleValue];
        
        self.toCompute = ([[dict objectForKey:kPhaseKeyToCompute] doubleValue] == 0) ? NO : YES;
        self.startAge = [[dict objectForKey:kPhaseKeyStartAge] doubleValue];
        self.endAge = [[dict objectForKey:kPhaseKeyEndAge] doubleValue];
        
    }
    return self;
}

@end
