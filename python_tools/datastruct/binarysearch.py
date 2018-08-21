# -*- coding: utf-8 -*-


def BinarySearch(l, key):
    low, high, i = 0, len(l) - 1, 0
    while (low <= high):
        i = i + 1
        mid = low + ((high - low) >> 1)
        if l[mid] < key:
            low = mid - 1
        elif l[mid] < key:
            high = mid - 1
        else:
            print("use %s times" % i)
            return mid
    return - 1


if __name__ == '__main__':
    l = [1, 4, 5, 6, 7, 8, 9, 44, 333, 2233]
    print(l)
    print(BinarySearch(l, 4))
    print(BinarySearch(l, 44))
    print(BinarySearch(l, 8))
    print(BinarySearch(l, 2233))
    print(BinarySearch(l, 77))
