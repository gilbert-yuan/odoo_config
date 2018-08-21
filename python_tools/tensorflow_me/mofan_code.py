#/usr/local/bin/python3
import tensorflow as tf
import numpy as np

#create data
x_data=np.random.rand(100).astype(np.float32)
y_data=x_data*0.1+0.3

#create tensorflow structure
Weights=tf.Variable(tf.random_uniform([1],-1.0,1.0)) #一维，范围[-1,1]
biases=tf.Variable(tf.zeros([1]))

y=Weights*x_data+biases

loss=tf.reduce_mean(tf.square(y-y_data))

#建立优化器，减小误差，提高参数准确度，每次迭代都会优化
optimizer=tf.train.GradientDescentOptimizer(0.5) #学习效率<1
train=optimizer.minimize(loss)

#初始化变量
init=tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init)
    #train
    for step in range(201):
        sess.run(train)
        if step%20==0:
            print(step,sess.run(Weights),sess.run(biases))
            
            
            
    """
            二、Session
            import tensorflow as tf
            matrix1 = tf.constant([[3, 3]])
            matrix2 = tf.constant([[2], [2]])
            # matrix multiply
            # np.dot(m1,m2)
            product = tf.matmul(matrix1, matrix2)
            # # method 1
            # sess = tf.Session()  # Session是一个object，首字母要大写
            # # 只有sess.run()之后，tensorflow才会执行一次
            # result = sess.run(product)
            # print(result)
            # # close 不影响，会显得更整洁
            # sess.close()
            # method 2
            # with 可以自己关闭会话
            with tf.Session() as sess:
                result2 = sess.run(product)
                print(result2)
            """         
            """三、Variable
                   import tensorflow as tf
                   state=tf.Variable(0,name='counter')
                   # print(state.name)
                   # 变量+常量=变量
                   one=tf.constant(1)
                   new_value=tf.add(state,one)
                   #将state用new_value代替
                   updata=tf.assign(state,new_value)
                   #变量必须要激活
                   init=tf.global_variables_initializer()
                   with tf.Session() as sess:
                       sess.run(init)
                       for _ in range(3):
                           sess.run(updata)
                           print(sess.run(state)
                    """
"""
四、placeholder
            运行到sess.run()的时候再给输入
            利用feed_dict绑定
            import tensorflow as tf
            # 给定type，tf大部分只能处理float32数据
            input1 = tf.placeholder(tf.float32)
            input2 = tf.placeholder(tf.float32)
            # Tensorflow 1.0 修改版
            # tf.mul---tf.multiply
            # tf.sub---tf.subtract
            # tf.neg---tf.negative
            output = tf.multiply(input1, input2)
            with tf.Session() as sess:
                # placeholder在sess.run()的时候传入值
                print(sess.run(output, feed_dict={input1: [7.], input2: [2.]}))
            
            五、激励函数
            解决非线性问题
            要求：必须可微分
            简单的神经网络一般可以使用任何激励函数；
            复杂的神经网络不能随意选择，会造成梯度爆炸和梯度消失的问题；
            简述激励函数：
            让某一部分的神经元先激活，传到后面的神经元，不同的神经元对不同的特征敏感。
            激活函数的输出：
            激活 / 抑制
            一般的神经网络：
            
            
            import tensorflow as tf
            import numpy as np

            def add_layer(inputs,in_size,out_size,activation_function=None):
                #Weights是一个矩阵，[行，列]为[in_size,out_size]
                Weights=tf.Variable(tf.random_normal([in_size,out_size]))#正态分布
                #初始值推荐不为0，所以加上0.1，一行，out_size列
                biases=tf.Variable(tf.zeros([1,out_size])+0.1)
                #Weights*x+b的初始化的值，也就是未激活的值
                Wx_plus_b=tf.matmul(inputs,Weights)+biases

                #激活

                if activation_function is None:
                    #激活函数为None，也就是线性函数
                    outputs=Wx_plus_b
                else:
                    outputs=activation_function(Wx_plus_b)
                return outputs
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
"""            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            