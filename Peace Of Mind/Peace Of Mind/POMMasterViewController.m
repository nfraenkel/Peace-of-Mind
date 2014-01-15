//
//  POMMasterViewController.m
//  Peace Of Mind
//
//  Created by Nathan Fraenkel on 1/8/14.
//  Copyright (c) 2014 Fraenkel Boys. All rights reserved.
//

#import "POMMasterViewController.h"

#import "POMDetailViewController.h"

@implementation POMMasterViewController

@synthesize singleton;

- (void)awakeFromNib
{
    [super awakeFromNib];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    
    // singleton
    self.singleton = [POMSingleton sharedDataModel];

	// pull to refresh
    UIRefreshControl *refreshControl = [[UIRefreshControl alloc] init];
    refreshControl.tintColor = [UIColor magentaColor];
    [refreshControl addTarget:self action:@selector(refresh) forControlEvents:UIControlEventValueChanged];
    self.refreshControl = refreshControl;
    
    // left and right buttons: edit, add
    self.navigationItem.leftBarButtonItem = self.editButtonItem;
    UIBarButtonItem *addButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemAdd target:self action:@selector(createNewScenario:)];
    self.navigationItem.rightBarButtonItem = addButton;
    
    // get scenarios!!
    [self getScenarios];
}

-(void)getScenarios {
    GetScenariosCommand *cmd = [[GetScenariosCommand alloc] initWithUserWithId:nil];
    cmd.delegate = self;
    [cmd fetchScenarios];
}

-(void)refresh {
    [self getScenarios];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (void)createNewScenario:(id)sender
{
    if (!singleton.scenarios) {
        singleton.scenarios = [[NSMutableArray alloc] init];
    }
    [self performSegueWithIdentifier:@"newScenario" sender:self];
}

#pragma mark - Table View

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return singleton.scenarios.count;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:@"ScenarioCell" forIndexPath:indexPath];

    UILabel *name = (UILabel*)[cell viewWithTag:1];
    UILabel *desc = (UILabel*)[cell viewWithTag:2];
    UILabel *comp = (UILabel*)[cell viewWithTag:3];
    
    Scenario *s = singleton.scenarios[indexPath.row];
    name.text = s.title;
    comp.text = (s.hasBeenComputed) ? [NSString stringWithFormat:@"$1,000.00"] : @"To Be Computed"; // TODO: fix once computed vs. not computed is done
    comp.textColor = (s.hasBeenComputed) ? [UIColor greenColor] : [UIColor redColor];
    desc.text = s.description;
    
    return cell;
}

- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the specified item to be editable.
    return YES;
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        [singleton.scenarios removeObjectAtIndex:indexPath.row];
        [tableView deleteRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationFade];
    } else if (editingStyle == UITableViewCellEditingStyleInsert) {
        // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view.
        NSLog(@"!!!!!!!!!!!!!! UITableViewCellEditingStyleInsert !!!!!!!!!!!!!!!!!");
    }
}


// Override to support rearranging the table view.
- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath
{
}

/*
// Override to support conditional rearranging of the table view.
- (BOOL)tableView:(UITableView *)tableView canMoveRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the item to be re-orderable.
    return YES;
}
*/

- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender
{
    if ([[segue identifier] isEqualToString:@"showScenarioDetail"]) {
        NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];
        Scenario *s = singleton.scenarios[indexPath.row];
        [[segue destinationViewController] setScenario:s];
    }
    else if ([[segue identifier] isEqualToString:@"newScenario"]) {
        UINavigationController *nav = (UINavigationController*)[segue destinationViewController];
        POMUpdateScenarioViewController *up = (POMUpdateScenarioViewController*)[nav topViewController];
        up.scenario = nil;
    }
}

#pragma mark - GetScenariosDelegate methods
-(void)reactToGetScenariosError:(NSError *)error {
    NSLog(@"[POMMasterViewController] GetScenarios ERROR: %@", error);
    
    [self.refreshControl endRefreshing];
    [self.tableView reloadData];
}

-(void)reactToGetScenariosResponse:(NSArray *)scenarios {
    NSLog(@"[POMMasterViewController] GetScenarios SUCCESS!!!");
    
    [self.singleton setScenarios:[NSMutableArray arrayWithArray:scenarios]];
    
    [self.refreshControl endRefreshing];
    [self.tableView reloadData];
}

@end
