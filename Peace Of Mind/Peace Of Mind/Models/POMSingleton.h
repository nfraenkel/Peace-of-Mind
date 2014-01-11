//
//  POMSingleton.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/10/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface POMSingleton : NSObject

@property (nonatomic, strong) NSMutableArray *scenarios;

+ (POMSingleton *) sharedDataModel;

//-(BOOL)isLoggedIn;



@end
