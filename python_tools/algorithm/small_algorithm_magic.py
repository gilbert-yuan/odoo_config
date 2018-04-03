# -*- coding:utf-8 -*-
from collections import defaultdict
import json
def count_byte_one(x, y):
    #     &	按位与运算符：参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0	(a & b) 输出结果 12 ，二进制解释： 0000 1100
    # |	按位或运算符：只要对应的二个二进位有一个为1时，结果位就为1。	(a | b) 输出结果 61 ，二进制解释： 0011 1101
    # ^	按位异或运算符：当两对应的二进位相异时，结果为1	(a ^ b) 输出结果 49 ，二进制解释： 0011 0001
    # ~	按位取反运算符：对数据的每个二进制位取反,即把1变为0,把0变为1 。~x 类似于 -x-1	(~a ) 输出结果 -61 ，二进制解释： 1100 0011，在一个有符号二进制数的补码形式。
    # <<	左移动运算符：运算数的各二进位全部左移若干位，由 << 右边的数字指定了移动的位数，高位丢弃，低位补0。	a << 2 输出结果 240 ，二进制解释： 1111 0000
    # >>	右移动运算符：把">>"左边的运算数的各二进位全部右移若干位，>> 右边的数字指定了移动的位数	a >> 2 输出结果 15 ，二进制解释： 0000 1111
    #    
     return bin(x^y).count("1")

 
def fuck(fn):
    print("fuck %s!" % fn.__name__[::-1].upper()) 
@fuck
def wfg():
    pass
    
def tree(): return defaultdict(tree)

if __name__=="__main__":
    print(count_byte_one(12, 6))
    categories = tree()
    categories['Programming Languages']['Python']
    categories['Python']['Standard Library']['sys']
    categories['Python']['Standard Library']['os']
    print(json.dumps(categories))
