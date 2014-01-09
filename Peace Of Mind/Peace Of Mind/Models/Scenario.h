//
//  Scenario.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "Phase.h"

@interface Scenario : NSObject

@property (nonatomic, strong) NSString *description, *email, *identifier, *title, *username;
@property (nonatomic, readwrite) BOOL hasBeenComputed;
@property (nonatomic, readwrite) double ageToday, inflationRate, lifeExpectancy, startingAmount, targetEndFunds;
@property (nonatomic, strong) NSArray *phaseList;

-(id)initWithDictionary:(NSDictionary*)dict;

@end
