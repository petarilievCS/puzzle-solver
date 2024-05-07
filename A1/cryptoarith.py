#**********************************************************************
#   cryptarith.py
#
#   UNSW CSE
#   COMP3411/9814
#   Code for Solving Cryptarithmetic Puzzles by Backtracking Search
#

import numpy as np
import sys

def main():
    add_string1, add_string2, sum_string = scan_puzzle()
    print(add_string1,'+',add_string2,'=',sum_string)
    var = []
    var, a1  = string2array(var,add_string1)
    var, a2  = string2array(var,add_string2)
    var, sum = string2array(var,sum_string)
    print('Variables:',end=' ')
    for k in range(len(var)-1):
        print(var[k],end=', ')
    print(var[len(var)-1])
    val = np.zeros(len(var),dtype=np.int32)
    search(0,a1,a2,sum,val,var)

#**********************************************************************
#   add new letters to var[], and create array a_num[] by replacing
#   each letter in a_string[] with its corresponding index in var[].
#
def string2array( var, a_string ):
    a_num = np.zeros(len(a_string),dtype=np.int32)
    for k in range(len(a_string)):
        j = 0
        while j < len(var) and var[j] != a_string[k]:
            j += 1
        if j == len(var):  # new letter
            var.append(a_string[k])
        a_num[k] = j
    return var, a_num

#**********************************************************************
#   scan a cryptarithmetic puzzle from stdin in the format:
#
#   SEND + MORE = MONEY
#    
def scan_puzzle():
    for line in sys.stdin:
        text = line.split()
        if len(text) >= 5:
            return text[0], text[2], text[4]
    print('Failed to scan puzzle.')
    exit(1)

#**********************************************************************
#   recursively apply backtracking search to find a solution.
#
def search( k, a1, a2, sum, val, var ):
    if( k == len(val)):
        if check_solution(a1,a2,sum,val):
            print_solution(a1,a2,sum,val,var)
    else:
        for d in range(0,10):
            j = 0
            while( j < k and val[j] != d ):
                j += 1
            if j == k:
                val[k] = d
                search(k+1,a1,a2,sum,val,var)

#**********************************************************************
#   check whether the current configuration is a valid solution.
#
def check_solution( a1, a2, sum, val ):
    if val[a1[0]] == 0 or val[a2[0]] == 0 or val[sum[0]] == 0:
        return False
    elif get_num(a1,val) + get_num(a2,val) == get_num(sum,val):
        return True
    else:
        return False

#**********************************************************************
#   print the solution that was found.
#
def print_solution( a1, a2, sum, val, var ):
    print(' Solution:',end=' ')
    k = len(val)
    for j in range(k-1):
        print(var[j],end=':')
        print(val[j],end=', ')
    print(var[k-1],end=':')
    print(val[k-1])
    print(get_num(a1,val),'+',get_num(a2,val),'=',get_num(sum,val))

#**********************************************************************
#   compute a decimal number from an array of indices and
#   an array of values.
#
def get_num( a, val ):
    num = 0
    for k in range(len(a)):
        num = 10*num + val[a[k]]
    return num


if __name__ == '__main__':
    main()
