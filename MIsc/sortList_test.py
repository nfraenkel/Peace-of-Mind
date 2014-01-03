#!flask/bin/python
'''
Test program to make sure the logic to extract the result from the MonteCarlo works properly
'''
import sys


origList = [10, 9, 8, 7, 1, 2, 3, 4, 5, 6 ]
SuccessRatio = 11
   
   
# ------------------
def findSuccess(inList, ratio):
    
    '''
    Find the value in the list such that 'ratio' % of the items in the list are smaller than it
    List is a list of float or int
    ratio is a % - between 0 and 100 
    '''
        
    # Sort the list
    inList.sort()
    # find the item that is small enough to succeed in SuccessRatio % of cases
    limitCnt = int (len(inList) * ratio * 0.01) - 1  # SuccessRatio is a %, account for index starting at 0
    if (limitCnt < 0):
        limitCnt = 0
    elif(limitCnt > len(inList) -1):
        limitCnt = len(inList) -1
    return (inList[limitCnt])

# ------------------
def main(argv):
    
    print ("Original List:")
    print (origList)
    
    for SuccessRatio in [1, 10, 11, 25, 50, 66, 80, 99, 100, 101]:
        print ('SuccessRatio = %d - Result = %d' % (SuccessRatio,findSuccess(origList, SuccessRatio)))
        
# ------------------

if __name__ == '__main__':
    main(sys.argv[1:])