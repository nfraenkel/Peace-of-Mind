//
//  POMSingleton.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "POMSingleton.h"

@implementation POMSingleton

@synthesize scenarios;

static POMSingleton *sharedDataModel = nil;

+ (POMSingleton *) sharedDataModel {
    @synchronized(self){
        if (sharedDataModel == nil){
            sharedDataModel = [[POMSingleton alloc] init];
        }
    }
    return sharedDataModel;
}

//-(BOOL)isLoggedIn {
//    return (self.email && ![self.email isEqualToString:@""] && self.authToken && ![self.authToken isEqualToString:@""]);
//}

@end
