#/usr/local/bin/python3
"""
一、前言
目前，深度学习已经广泛应用于各个领域，比如图像识别，图形定位与检测，语音识别，机器翻译等等，
对于这个神奇的领域，很多童鞋想要一探究竟，这里抛砖引玉的简单介绍下最火的深度学习开源框架 tensorflow。
本教程不是 cookbook，所以不会将所有的东西都事无巨细的讲到，所有的示例都将使用 python。
那么本篇教程会讲到什么？首先是一些基础概念，包括计算图，graph 与 session，基础数据结构，
Variable，placeholder 与 feed_dict 以及使用它们时需要注意的点。最后给出了在 tensorflow 中建立一个机器学习模型步骤，并用一个手写数字识别的例子进行演示。
1、 tensorflow是什么？
tensorflow 是 google 开源的机器学习工具，在2015年11月其实现正式开源，开源协议Apache 2.0。
下图是 query 词频时序图，从中可以看出 tensorflow 的火爆程度。
2、 why tensorflow?

Tensorflow 拥有易用的 python 接口，而且可以部署在一台或多台 cpu , gpu 上，兼容多个平台，包括但不限于 
安卓/windows/linux 等等平台上，而且拥有 tensorboard这种可视化工具，可以使用 checkpoint 进行实验管理，
得益于图计算，它可以进行自动微分计算，拥有庞大的社区，而且很多优秀的项目已经使用 tensorflow 进行开发了。
3、 易用的tensorflow工具
如果不想去研究 tensorflow 繁杂的API,仅想快速的实现些什么，可以使用其他高层工具。比如 tf.contrib.learn，
tf.contrib.slim，Keras 等，它们都提供了高层封装。这里是 tflearn 的github样例集。
4、 tensorflow安装
目前 tensorflow 的安装已经十分方便，有兴趣可以参考官方文档。
二、 tensorflow基础
       实际上编写tensorflow可以总结为两步.
       （1）组装一个graph;
       （2）使用session去执行graph中的operation。
       因此我们从 graph 与 session 说起。
1、 graph与session
（1）计算图
Tensorflow 是基于计算图的框架，因此理解 graph 与 session 显得尤为重要。
不过在讲解 graph 与 session 之前首先介绍下什么是计算图。假设我们有这样一个需要计算的表达式。
该表达式包括了两个加法与一个乘法，为了更好讲述引入中间变量c与d。由此该表达式可以表示为：
当需要计算e时就需要计算c与d，而计算c就需要计算a与b，计算d需要计算b。
这样就形成了依赖关系。这种有向无环图就叫做计算图，因为对于图中的每一个节点其微分都很容易得出，
因此应用链式法则求得一个复杂的表达式的导数就成为可能，所以它会应用在类似tensorflow这种需要应用反向传播算法的框架中。

（2）概念说明

下面是 graph , session , operation , tensor 四个概念的简介。

Tensor：类型化的多维数组，图的边；

Operation:执行计算的单元，图的节点；

Graph：一张有边与点的图，其表示了需要进行计算的任务；

Session:称之为会话的上下文，用于执行图。

Graph仅仅定义了所有 operation 与 tensor 流向，没有进行任何计算。而session根据 graph 的定义分配资源，
计算 operation，得出结果。既然是图就会有点与边，在图计算中 operation 就是点而 tensor 就是边。
Operation 可以是加减乘除等数学运算，也可以是各种各样的优化算法。每个 operation 都会有零个或多个输入，零个或多个输出。
 tensor 就是其输入与输出，其可以表示一维二维多维向量或者常量。而且除了Variables指向的 tensor 外所有的 tensor 在流入下一个节点后都不再保存。

（3）举例

下面首先定义一个图（其实没有必要，tensorflow会默认定义一个），并做一些计算。

"""
import tensorflow as tf
graph = tf.Graph()
with graph.as_default():
    foo = tf.Variable(3, name='foo')
    bar = tf.Variable(2, name='bar')
    result = foo + bar
    initialize = tf.global_variables_initializer()
print(result)
"""
这段代码，首先会载入tensorflow，定义一个graph类，
并在这张图上定义了foo与bar的两个变量，最后对这个值求和，并初始化所有变量。
其中，Variable是定义变量并赋予初值。让我们看下result（最后1行代码）。
后面是输出，可以看到并没有输出实际的结果，由此可见在定义图的时候其实没有进行任何实际的计算。
"""
with tf.Session(graph=graph) as sess:
    sess.run(initialize)
    res = sess.run(result)
print(res)
"""
这段代码中，定义了session，并在session中执行了真正的初始化，并且求得result的值并打印出来。
可以看到，在session中产生了真正的计算，得出值为5。
"""

#2、数据结构

"""
Tensorflow的数据结构有着rank,shape,data types的概念，下面来分别讲解。
（1）rank
Rank一般是指数据的维度，其与线性代数中的rank不是一个概念。其常用rank举例如下。

（2）shape

Shape指tensor每个维度数据的个数，可以用python的list/tuple表示。下图表示了rank,shape的关系。

（3）data type

Data type，是指单个数据的类型。常用DT_FLOAT，也就是32位的浮点数。下图表示了所有的types。

3、 Variables

（1）介绍

当训练模型时，需要使用Variables保存与更新参数。Variables会保存在内存当中，
所有tensor一旦拥有Variables的指向就不会在session中丢失。其必须明确的初始化而且可以通过Saver保存到磁盘上。
Variables可以通过Variables初始化。
weights = tf.Variable(tf.random_normal([784, 200], stddev=0.35),name="weights")
biases = tf.Variable(tf.zeros([200]), name="biases")

<<<<<<< Local Changes
其中，tf.random_normal是随机生成一个正态分布的tensor，
其shape是第一个参数，stddev是其标准差。tf.zeros是生成一个全零的tensor。之后将这个tensor的值赋值给Variable。


=======
其中，tf.random_normal是随机生成一个正态分布的tensor，其shape是第一个参数，stddev是其标准差。
tf.zeros是生成一个全零的tensor。之后将这个tensor的值赋值给Variable。
>>>>>>> External Changes


（2）初始化

实际在其初始化过程中做了很多的操作，比如初始化空间，赋初值（等价于tf.assign），并把Variable添加到graph中等操作。
注意在计算前需要初始化所有的Variable。一般会在定义graph时定义global_variables_initializer，其会在session运算时初始化所有变量。

直接调用global_variables_initializer会初始化所有的Variable，如果仅想初始化部分Variable可以调用tf.variables_initializer。
Init_ab = tf.variables_initializer([a,b],name=”init_ab”)

Variables可以通过eval显示其值，也可以通过assign进行赋值。Variables支持很多数学运算，具体可以参照官方文档。




（3）Variables与constant的区别

值得注意的是Variables与constant的区别。Constant一般是常量，可以被赋值给Variables，
constant保存在graph中，如果graph重复载入那么constant也会重复载入，其非常浪费资源，如非必要尽量不使用其保存大量数据。
而Variables在每个session中都是单独保存的，甚至可以单独存在一个参数服务器上。可以通过代码观察到constant实际是保存在graph中，具体如下。

const = tf.constant(1.0,name="constant")
print(tf.get_default_graph().as_graph_def())
这里第二行是打印出图的定义，其输出如下：
node {
       name: "constant"
       op: "Const"
       attr {
          key: "dtype"
       value {
          type: DT_FLOAT
      }
  }
  attr {
    key: "value"
    value {
      tensor {
        dtype: DT_FLOAT
        tensor_shape {
        }
        float_val: 1.0
      }
    }
  }
}
versions {
  producer: 17
}

4）命名

另外一个值得注意的地方是尽量每一个变量都明确的命名，这样易于管理命令空间，而且在导入模型的时候不会造成不同模型之间的命名冲突，
这样就可以在一张graph中容纳很多个模型。

4、 placeholders与feed_dict

当我们定义一张graph时，有时候并不知道需要计算的值，比如模型的输入数据，其只有在训练与预测时才会有值。这时就需要placeholder与feed_dict的帮助。

定义一个placeholder，可以使用tf.placeholder(dtype,shape=None,name=None)函数。

foo = tf.placeholder(tf.int32,shape=[1],name='foo')
bar = tf.constant(2,name='bar')
result = foo + bar
with tf.Session() as sess:
   print(sess.run(result)) 

在上面的代码中，会抛出错误（InvalidArgumentError），因为计算result需要foo的具体值，而在代码中并没有给出。这时候需要将实际值赋给foo。
最后一行修改如下（其中最后的dict就是一个feed_dict，一般会使用python读入一些值后传入，当使用minbatch的情况下，每次输入的值都不同）：

print(sess.run(result,{foo:[3]}))

"""









