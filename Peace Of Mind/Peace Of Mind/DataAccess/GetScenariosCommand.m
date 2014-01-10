//
//  GetScenariosCommand.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "GetScenariosCommand.h"

@implementation GetScenariosCommand

@synthesize userId, delegate;

-(id)initWithUserWithId:(NSString *)IdOfUser {
    self = [super init];
    if (self) {
        // custom initialization
        self.userId = IdOfUser;
    }
    return self;
}

-(void)fetchScenarios {
    NSLog(@"[GetScenariosCommand] fetching scenarios for user.....");
    
    // spinnaz
    [UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
    
    // set URL
    NSString *url = [NSString stringWithFormat:@"%@/finplan/api/v2.0/finplan", HOST];
    
    // HTTP request, setting stuff
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:url] cachePolicy:NSURLRequestUseProtocolCachePolicy timeoutInterval:10];
    [request setHTTPMethod:@"GET"];
    [request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
    
    
    // start connection
    NSURLConnection *connection = [[NSURLConnection alloc] initWithRequest:request delegate:self];
    [connection start];
}

#pragma mark connection protocol functions
- (void)connection:(NSURLConnection *)connection didReceiveResponse:(NSURLResponse *)response {
    NSLog(@"[GetScenariosCommand] conection did receive response!");
    _data = [[NSMutableData alloc] init];
    
}

- (void)connection:(NSURLConnection *)connection didReceiveData:(NSData *)data {
    NSLog(@"[GetScenariosCommand] conection did receive data!");
    [_data appendData:data];
}

- (void)connection:(NSURLConnection *)connection didFailWithError:(NSError *)error {
    // Please do something sensible here, like log the error.
    NSLog(@"[GetScenariosCommand] connection failed with error: %@", error.description);
    
    // stop spinners
    [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
    
    [self.delegate reactToGetScenariosError:error];
}

- (void)connectionDidFinishLoading:(NSURLConnection *)connection {
    NSLog(@"[GetScenariosCommand] connectiondidfinishloading!");
    [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
    
    //    NSString *responseString = [[NSString alloc] initWithData:_data encoding:NSUTF8StringEncoding];
    //    NSLog(@"response data: %@", responseString);
    
    NSDictionary *dictResponse = [NSJSONSerialization JSONObjectWithData:_data options:0 error:nil];
    
    NSDictionary *financialPlans = [dictResponse objectForKey:kResponseDictionaryKey];
    
    NSMutableArray *scenarios = [[NSMutableArray alloc] init];
    for (NSDictionary *dict in financialPlans){
        NSLog(@"dict? %@", dict);
        Scenario *s = [[Scenario alloc] initWithDictionary:dict];
        [scenarios addObject:s];
    }

    [self.delegate reactToGetScenariosResponse:[NSArray arrayWithArray:scenarios]];
    
}



@end