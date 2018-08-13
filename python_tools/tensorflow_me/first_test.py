#/usr/local/bin/python3
import tensorflow as tf
import numpy as np

# 使用Numpy 生成假数据（phony data） 总共100个点
x_data = np.float32(np.random.rand(2, 100)) # 随机输入
y_data = np.dot([0.100, 0.200], x_data) + 0.300

#构造一个线性模型
#
b = tf.Variable(tf.zeros([1]))
W = tf.Variable(tf.random_uniform([1, 2], -1.0, 1.0))
# tf.random_uniform((6, 6), minval=low,maxval=high,dtype=tf.float32)))返回6*6的矩阵，产生于low和high之间，产生的值是均匀分布的。
y = tf.matmul(W, x_data) + b
# tf.mul(a,b) 这里的矩阵a和矩阵b的shape必须相等 tf.mul()是矩阵的element-wise相乘（即Hadamard乘积）
# tf.matmul(a,b) 这里的矩阵a和矩阵b的shape应是a的行数对等与b的列数，tf.matmul()是矩阵的一般相乘。
# 最小方差
loss = tf.reduce_mean(tf.square(y - y_data))
# 在计算损失时，通常会用到reduce_sum()函数来进行求和，但是在使用过程中常常会搞不清楚具体是怎样进行计算的，通过查阅资料，
# 逐渐搞清楚了这个函数的用法，下面就来详细解释一下。

#看到这里，函数名的前缀为什么是reduce_其实也就很容易理解了，
# reduce就是“对矩阵降维”的含义，下划线后面的部分就是降维的方式，
# 在reduce_sum()中就是按照求和的方式对矩阵降维。那么其他reduce前缀的函数也举一反三了，
# 比如reduce_mean()就是按照某个维度求平均值，等等。
#

optimzer = tf.train.GradientDescentOptimizer(0.5)
train = optimzer.minimize(loss)
#初始化变量
init = tf.initialize_all_variables()
#启动图（graph）
sess = tf.Session()
sess.run(init)
# 拟合平面
for step in range(0, 201):
    sess.run(train)
    if step % 20 == 0:
        print( step, sess.run(W), sess.run(b))
#得到最佳拟合效果 W: [[0.100  0.200]], b: [0.300]

# tf.zeros
# 生成为零的数组
#
#

#  tf.Variable
# 训练模型时，需要使用变量(Variables)保存和更新参数。Variables是包含张量(tensor)的内存缓冲。变量必须要先被初始化(initialize)，而且可以在训练时和训练后保存(save)到磁盘中。之后可以再恢复(restore)保存的变量值来训练和测试模型。
# 主要参考一下两类：
# - The tf.Variable class.
# - The tf.train.Saver class.



