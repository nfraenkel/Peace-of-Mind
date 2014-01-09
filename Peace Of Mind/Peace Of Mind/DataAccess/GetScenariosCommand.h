//
//  GetScenariosCommand.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "Scenario.h"

@protocol GetScenariosDelegate <NSObject>
-(void)reactToGetScenariosResponse:(NSArray*)scenarios;
-(void)reactToGetScenariosError:(NSError*)error;
@end

@interface GetScenariosCommand : NSObject <NSURLConnectionDataDelegate> {
    NSArray *scenariosFromResponse;
    NSMutableData *_data;
}

@property (nonatomic, strong) NSString *userId;;
@property (nonatomic, strong) id<GetScenariosDelegate> delegate;

-(id)initWithUserWithId:(NSString*)IdOfUser;
-(void)fetchScenarios;

@end

