//
//  Scenario.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "Scenario.h"

@implementation Scenario

@synthesize description, email, identifier, title, username;
@synthesize hasBeenComputed;
@synthesize ageToday, inflationRate, lifeExpectancy, startingAmount, targetEndFunds;

-(id)initWithDictionary:(NSDictionary*)dict {
    self = [super init];
    if (self) {
        // custom init
        self.description = [dict objectForKey:kScenarioKeyDescription];
        self.ageToday = [[dict objectForKey:kScenarioKeyAgeToday] doubleValue];
        self.email = [dict objectForKey:kScenarioKeyEmail];
        self.identifier = [dict objectForKey:kScenarioKeyIdentifier];
        self.hasBeenComputed = ([[dict objectForKey:kScenarioKeyHasResult] integerValue] == 0) ? NO : YES;
        self.inflationRate = [[dict objectForKey:kScenarioKeyInflationRate] doubleValue];
        self.lifeExpectancy = [[dict objectForKey:kScenarioKeyLifeExpectancy] doubleValue];
        self.phaseList = [self createPhaseListFromArray:[dict objectForKey:kScenarioKeyPhaseList]];
        self.startingAmount = [[dict objectForKey:kScenarioKeyStartingAmount] doubleValue];
        self.targetEndFunds = [[dict objectForKey:kScenarioKeyTargetFunds] doubleValue];
        self.title = [dict objectForKey:kScenarioKeyTitle];
        self.username = [dict objectForKey:kScenarioKeyUsername];
    }
    return self;
}

-(NSArray*)createPhaseListFromArray:(NSArray*)array {
    NSMutableArray *phases = [[NSMutableArray alloc] init];
    for (NSDictionary *dict in array) {
        Phase *p = [[Phase alloc] initWithDictionary:dict];
        [phases addObject:p];
    }
    return phases;
}

@end
