//
//  POMDetailViewController.h
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface POMDetailViewController : UIViewController

@property (strong, nonatomic) id detailItem;

@property (weak, nonatomic) IBOutlet UILabel *detailDescriptionLabel;
@end
