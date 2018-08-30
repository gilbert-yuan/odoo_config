# -*- coding:utf-8 -*-
"""
http://www.jiuzhang.com/tutorial/bit-manipulation/84
"""
def left_move(num, step):
    # 可以看出，左移操作的结果“几乎”等于A * 2^B（如果不溢出的情况下）。
    # 因为位移运算比乘法和求幂的运算快很多很多
    #     (13)10 << 3 = (1101)2 << 3 = (1101000)2 = (104)10
    # 3 << 1 = 6
    # 2147483647 << 1 = -2 可能会溢出，因为python 是弱类型语言 所以
    return_val = num << step
    return return_val
def right_move(num, step):
    return_val = num >> step
    return return_val

def logic_right_move(num, step):
    # python 没有区分 逻辑右移 还是 算术右移
    return_val = num >> step
    return return_val

def byte_and():
    # 1 & 1 = 1
    # 1 & 0 = 0
    # 0 & 1 = 0
    # 0 & 0 = 0
    pass

def byte_or():
    # 1 | 1 = 1
    # 1 | 0 = 1
    # 0 | 1 = 1
    # 0 | 0 = 0
    pass

def byte_not():
    # A =   (1)10 = (00000000000000000000000000000001)2
    # ~A = ~ (1)10 = (11111111111111111111111111111110)2 = (-2)10
    pass

def byte_different():
    # 应用一：数组中，只有一个数出现一次，剩下都出现两次，找出出现一次的数
    # http://www.lintcode.com/en/problem/single-number/
    # 因为只有一个数恰好出现一个，剩下的都出现过两次，所以只要将所有的数异或起来，就可以得到唯一的那个数，因为相同的数出现的两次，异或两次等价于没有任何操作！
    # a ^ b ^ b = a // 对一个数异或两次等价于没有任何操作！
    # 1 ^ 1 = 0
    # 1 ^ 0 = 1
    # 0 ^ 1 = 1
    # 0 ^ 0 = 0 #
    pass 
        
"""
位运算基本应用1
教程
问答(3)
应用一：给出两个32位的整数N和M，以及两个二进制位的位置i和j。写一个方法来使得N中的第i到j位等于M（M会是N中从第i为开始到第j位的子串)
http://www.lintcode.com/en/problem/update-bits/

举个例子

n = (1024)10 = (00000000000000000000010000000000)2; // 我们这里用32位表述
m =   (21)10 = (00000000000000000000000000010101)2; // 1 + 4 + 16 = 21, 这里同样我们用32位表述
i = 2, j = 6,

那么根据题目，我们希望最终得到的结果是`(00000000000000000000010001010100)2` = `(1108)10`
根据题意，有一个想法，将n中第i位到第j位先置为0，然后，按位或上m << i即可。

现在问题是如何将n中第i位到第j位置为0 ? 可以考虑构造一个数，这个数从第i位到第j位是0，其他位都为1。然后这个数和n与一下，就可以把n的i~j位置成0了。
虽然这样的数并不是很好构造，反过来思考我们构造一个数从第i位到第j位都是1，其他位为0的数，然后将这个数取反，就可以得到从第i位到第j位是0，其他位是1的数。
-1的二进制表示是所有位为1 (这一点很重要，32位全是1的二进制对应整数-1.)，我们以这个数为起点，需要的做的是将高(31-j)位置0，将低i位置0. 按照例子中i = 2, j = 6, 所以我们需要把-1看成全是1的二进制表示，然后把高(31 - 6) = 25位全部置成0，低2位也置成0。
(-1)10 = (11111111111111111111111111111111)2, 把-1的前面25位和后面2位置成0之后，结果为
       =>(00000000000000000000000001111100)2
所以具体的操作应该是这样的：
将-1先左移(31-j)位，因为高(31-j)位都是不需要的：

(-1)10 << (31 - 6) = (-1) << 25 = (11111110000000000000000000000000)2 = (-33554432)10
然后再在这个基础上逻辑右移(31 - j + i)位，因为要将低i位置0：

(-33554432)10 >>> (31 - 6 + 2) = (00000000000000000000000000011111)2 = (31)10 
你可以思考一下为什么前面我们需要27个0 ？
你还可以思考一下，这里为什么要用逻辑右移 ？
最后我们左移i位，这里也就是左移2位，将1恢复到正确的位置即可。即得到第i位到第j位是1，其他位是0的数。

(31)10 << 2 = (00000000000000000000000000011111)2 << 2 = (00000000000000000000000001111100)2 = (124)10



位运算基本应用2
教程
问答(1)
应用二：给出两个整数a和b, 求他们的和, 但不能使用 + 等数学运算符
http://www.lintcode.com/zh-cn/problem/a-b-problem/

主要利用异或运算来完成，异或运算有一个别名叫做：不进位加法，我们在前面的基本运算第二章中有提到过。
那么a ^ b就是a和b相加之后，该进位的地方不进位的结果，相信这一点大家没有疑问，但是需要注意的是，这个加法是在二进制下完成的加法。
然后下面考虑哪些地方要进位？

什么地方需要进位呢？ 自然是a和b里都是1的地方
a & b就是a和b里都是1的那些位置，那么这些位置左边都应该有一个进位1，a & b << 1 就是进位的数值(a & b的结果所有左移一位)。

那么我们把不进位的结果和进位的结果加起来，就是实际中a + b的和。

a + b = (a ^ b) + (a & b << 1)
令
a' = a ^ b, b' = (a & b) << 1 => a + b = (a ^ b) + (a & b << 1) = a' + b'

技巧一：消去二进制中最右侧的那个1
教程
问答(1)
x & (x - 1) 用于消去x最后一位的1, 比如x = 12, 那么在二进制下就是(1100)2

x           = 1100
x - 1       = 1011
x & (x - 1) = 1000

# 应用一：用 O(1) 时间检测整数 n 是否是 2 的幂次。
# http://www.lintcode.com/zh-cn/problem/o1-check-power-of-2/

# N如果是2的幂次，则N满足两个条件。

# N > 0
# N的二进制表示中只有一个1, 注意只能有1个。
# 因为N的二进制表示中只有一个1，所以使用N & (N - 1)将N唯一的一个1消去，应该返回0。

# 综合上述方法，我们可以写出非常简洁漂亮的Java代码：

# class Solution {
# public:
#     /*
#      * @param n: An integer
#      * @return: True or false
#      */
#     bool checkPowerOf2(int n) {
#         // write your code here
#         return n > 0 && (n & (n - 1)) == 0;
#     }
# };


# 应用二：计算在一个 32 位的整数的二进制表式中有多少个 1.
# http://www.lintcode.com/zh-cn/problem/count-1-in-binary/

# 由x & (x - 1)消去x最后一位的1可知。不断使用 x & (x - 1) 消去x最后一位的1，计算总共消去了多少次即可。

# public class Solution {
#     /**
#      * @param num: an integer
#      * @return: an integer, the number of ones in num
#      */
#     public int countOnes(int num) {
#         int count = 0;
#         while (num != 0) {
#             num = num & (num - 1);
#             count++;
#         }
#         return count;
#     }
# }
#
# 

应用三：如果要将整数A转换为B，需要改变多少个bit位？
http://www.lintcode.com/zh-cn/problem/flip-bits/

这个应用是上面一个应用的拓展
思考将整数A转换为B，如果A和B在第i（0 <=i < 32）个位上相等，则不需要改变这个BIT位，如果在第i位上不相等，则需要改变这个BIT位。

所以问题转化为了A和B有多少个BIT位不相同！
联想到位运算有一个异或操作，相同为0，相异为1，所以问题转变成了计算A异或B之后这个数中1的个数!

class Solution {
    /**
     *@param a, b: Two integer
     *return: An integer
     */
    public int countOnes(int num) {
        int count = 0;
        while (num != 0) {
            num = num & (num - 1);
            count++;
        }
        return count;
    }

    public int bitSwapRequired(int a, int b) {
        // write your code here
        return countOnes(a ^ b);
    }
};


应用：给定一个含不同整数的集合，返回其所有的子集
http://www.lintcode.com/zh-cn/problem/subsets/

思路就是使用一个正整数二进制表示的第i位是1还是0来代表集合的第i个数取或者不取。
所以从0到2^n-1总共2^n个整数，正好对应集合的2^n个子集。如下是就是 整数 <=> 二进制 <=> 对应集合 之间的转换关系。

S = {1,2,3}

N bit Combination
0 000 {}
1 001 {1}
2 010 {2}
3 011 {1,2}
4 100 {3}
5 101 {1,3}
6 110 {2,3}
7 111 {1,2,3}

a ^ b ^ b = a // 对一个数异或两次等价于没有任何操作！
应用一：数组中，只有一个数出现一次，剩下都出现两次，找出出现一次的数
http://www.lintcode.com/en/problem/single-number/

因为只有一个数恰好出现一个，剩下的都出现过两次，所以只要将所有的数异或起来，就可以得到唯一的那个数，因为相同的数出现的两次，异或两次等价于没有任何操作！

public class Solution {
    public int singleNumber(int[] nums) {
        int result = 0, n = nums.length;
        for (int i = 0; i < n; i++)
        {
            result ^= nums[i];
        }
        return result;
    }
}
应用二：数组中，只有一个数出现一次，剩下都出现三次，找出出现一次的数
http://www.lintcode.com/en/problem/single-number-ii/

因为其他数是出现三次的，也就是说，对于每一个二进制位，如果只出现一次的数在该二进制位为1，那么这个二进制位在全部数字中出现次数无法被3整除。
对于每一位，我们让Two，One表示当前位的状态。

我们看Two和One里面的每一位的定义，对于ith(表示第i位)：

如果Two里面ith是1，则ith当前为止出现1的次数模3的结果是2
如果One里面ith是1，则ith目前为止出现1的次数模3的结果是1
注意Two和One里面不可能ith同时为1，因为这样就是3次，每出现3次我们就可以抹去（消去）。那么最后One里面存储的就是每一位模3是1的那些位，综合起来One也就是最后我们要的结果。

如果B表示输入数字的对应位，Two+和One+表示更新后的状态
那么新来的一个数B，此时跟原来出现1次的位做一个异或运算，&上~Two的结果(也就是不是出现2次的)，那么剩余的就是当前状态是1的结果。
同理Two ^ B （2次加1次是3次，也就是Two里面ith是1，B里面ith也是1，那么ith应该是出现了3次，此时就可以消去，设置为0），我们相当于会消去出现3次的位。

但是Two ^ B也可能是ith上Two是0，B的ith是1，这样Two里面就混入了模3是1的那些位！！！怎么办？我们得消去这些！我们只需要保留不是出现模3余1的那些位ith，而One是恰好保留了那些模3余1次数的位，`取反不就是不是模3余1的那些位ith么？最终对(~One+)取一个&即可。
综合起来就是：

One+ = (One ^ B) & (~Two)
Two+ = (~One+) & (Two ^ B)
以下就是非常漂亮的Java代码实现：

public class Solution {
    public int singleNumber(int[] nums) {
        int ones = 0, twos = 0;
        for(int i = 0; i < nums.length; i++){
            ones = (ones ^ nums[i]) & ~twos;
            twos = (twos ^ nums[i]) & ~ones;
        }
        return ones;
    }
}


应用三：数组中，只有两个数出现一次，剩下都出现两次，找出出现一次的这两个数
http://www.lintcode.com/en/problem/single-number-iii/

有了第一题的基本的思路，我们可以将数组分成两个部分，每个部分里只有一个元素出现一次，其余元素都出现两次。那么使用这种方法就可以找出这两个元素了。不妨假设出现一个的两个元素是x，y，那么最终所有的元素异或的结果就是等价于res = x^y。
并且res！=0

为什么呢？ 如果res 等于0，则说明x和y相等了！！！！
因为res不等于0，那么我们可以一定可以找出res二进制表示中的某一位是1。

对于x和y，一定是其中一个这一位是1，另一个这一位不是1！！！细细琢磨， 因为如果都是0或者都是1，怎么可能异或出1
对于原来的数组，我们可以根据这个位置是不是1就可以将数组分成两个部分。x，y一定在不同的两个子集中。

而且对于其他成对出现的元素，要么都在x所在的那个集合，要么在y所在的那个集合。对于这两个集合我们分别求出单个出现的x 和 单个出现的y即可。
public class Solution {
    public int[] singleNumber(int[] nums) {
        //用于记录，区分“两个”数组
        int diff = 0;
        for(int i = 0; i < nums.length; i ++) {
            diff ^= nums[i];
        }
        //取最后一位1
        //先介绍一下原码，反码和补码
        //原码，就是其二进制表示（注意，有一位符号位）
        //反码，正数的反码就是原码，负数的反码是符号位不变，其余位取反
        //补码，正数的补码就是原码，负数的补码是反码+1
        //在机器中都是采用补码形式存
        //diff & (-diff)就是取diff的最后一位1的位置
        diff &= -diff;
        
        int[] rets = {0, 0}; 
        for(int i = 0; i < nums.length; i ++) {
            //分属两个“不同”的数组
            if ((nums[i] & diff) == 0) {
                rets[0] ^= nums[i];
            }
            else {
                rets[1] ^= nums[i];
            }
        }
        return rets;
    }
}
"""

def a_puls_b(a, b):
    # a 加 b 但是不能用加减等运算符
    return (a ^ b) + (a & b << 1)

def count_one(num):
    count = 0
    while num != 0:
        num = num & (num - 1)
        count += 1
    return count

if __name__ == '__main__':
    print(right_move(6, 3), '=====')
    print(right_move(-127 , 2), '=====')
    print(logic_right_move(-127 , 2), '=====')
    print(a_puls_b(127 , 2), '=====')

