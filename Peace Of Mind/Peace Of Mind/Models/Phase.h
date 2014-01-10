//
//  Phase.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/9/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface Phase : NSObject

@property (nonatomic, strong) NSString *name;
@property (nonatomic, readwrite) double netContribution, bondsPercentage, cashPercentage, stocksPercentage, tBillsPercentage, endAge, startAge;
@property (nonatomic, readwrite) BOOL toCompute;

-(id)initWithDictionary:(NSDictionary*)dict;

@end
