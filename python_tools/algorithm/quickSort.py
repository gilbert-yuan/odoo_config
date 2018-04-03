# -*- coding:utf-8 -*-
import random
def fast_sorted(L):
    if len(L)< 2: return L
    pivot_element = random.choice(L)
    small = [i for i in L if i < pivot_element]
    medium = [i for i in L if i == pivot_element]
    large = [i for i in L if i > pivot_element]
    return fast_sorted(small) + medium + fast_sorted(large)

if __name__ == '__main__':
    L = [2,3,5,22,45,7,5,34,34544,565689,87,32,4,5,8,899]
    print( fast_sorted(L))
