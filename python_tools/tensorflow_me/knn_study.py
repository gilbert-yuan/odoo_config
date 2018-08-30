"""
k-近邻（kNN, k-NearestNeighbor）算法是一种基本分类与回归方法，我们这里只讨论分类问题中的 k-近邻算法。

一句话总结：近朱者赤近墨者黑！

k 近邻算法的输入为实例的特征向量，对应于特征空间的点；输出为实例的类别，可以取多类。k 近邻算法假设给定一个训练数据集，其中的实例类别已定。分类时，对新的实例，根据其 k 个最近邻的训练实例的类别，通过多数表决等方式进行预测。因此，k近邻算法不具有显式的学习过程。

k 近邻算法实际上利用训练数据集对特征向量空间进行划分，并作为其分类的“模型”。 k值的选择、距离度量以及分类决策规则是k近邻算法的三个基本要素。



KNN 工作原理

假设有一个带有标签的样本数据集（训练样本集），其中包含每条数据与所属分类的对应关系。
输入没有标签的新数据后，将新数据的每个特征与样本集中数据对应的特征进行比较。
计算新数据与样本数据集中每条数据的距离。
对求得的所有距离进行排序（从小到大，越小表示越相似）。
取前 k （k 一般小于等于 20 ）个样本数据对应的分类标签。
求 k 个数据中出现次数最多的分类标签作为新数据的分类。
KNN 通俗理解

给定一个训练数据集，对新的输入实例，在训练数据集中找到与该实例最邻近的 k 个实例，这 k 个实例的多数属于某个类，就把该输入实例分为这个类。

KNN 开发流程

收集数据：任何方法
准备数据：距离计算所需要的数值，最好是结构化的数据格式
分析数据：任何方法
训练算法：此步骤不适用于 k-近邻算法
测试算法：计算错误率
使用算法：输入样本数据和结构化的输出结果，然后运行 k-近邻算法判断输入数据分类属于哪个分类，最后对计算出的分类执行后续处理
KNN 算法特点

优点：精度高、对异常值不敏感、无数据输入假定
缺点：计算复杂度高、空间复杂度高
适用数据范围：数值型和标称型
"""
#/usr/local/bin/python3
def file2matrix(filename):
   """
   Desc:
       导入训练数据
   parameters:
       filename: 数据文件路径
   return: 
       数据矩阵 returnMat 和对应的类别 classLabelVector
   """
   fr = open(filename)
   # 获得文件中的数据行的行数
   numberOfLines = len(fr.readlines())
   # 生成对应的空矩阵
   # 例如：zeros(2，3)就是生成一个 2*3的矩阵，各个位置上全是 0 
   returnMat = zeros((numberOfLines, 3))  # prepare matrix to return
   classLabelVector = []  # prepare labels return
   fr = open(filename)
   index = 0
   for line in fr.readlines():
       # str.strip([chars]) --返回已移除字符串头尾指定字符所生成的新字符串
       line = line.strip()
       # 以 '\t' 切割字符串
       listFromLine = line.split('\t')
       # 每列的属性数据
       returnMat[index, :] = listFromLine[0:3]
       # 每列的类别数据，就是 label 标签数据
       classLabelVector.append(int(listFromLine[-1]))
       index += 1
   # 返回数据矩阵returnMat和对应的类别classLabelVector
   return returnMat, classLabelVector



def classifyPerson():
    resultList = ['not at all', 'in small doses', 'in large doses']
    percentTats = float(raw_input("percentage of time spent playing video games ?"))
    ffMiles = float(raw_input("frequent filer miles earned per year?"))
    iceCream = float(raw_input("liters of ice cream consumed per year?"))
    datingDataMat, datingLabels = file2matrix('datingTestSet2.txt')
    normMat, ranges, minVals = autoNorm(datingDataMat)
    inArr = array([ffMiles, percentTats, iceCream])
    classifierResult = classify0((inArr-minVals)/ranges,normMat,datingLabels, 3)
    print "You will probably like this person: ", resultList[classifierResult - 1]
"""
    训练算法：此步骤不适用于 k-近邻算法

    因为测试数据每一次都要与全量的训练数据进行比较，所以这个过程是没有必要的。

    kNN 算法伪代码：

    对于每一个在数据集中的数据点：
        计算目标的数据点（需要分类的数据点）与该数据点的距离
        将距离排序：从小到大
        选取前K个最短距离
        选取这K个中最多的分类类别
        返回该类别来作为目标数据点的预测值
    
    """
def datingClassTest():
    """
    Desc:
        对约会网站的测试方法
    parameters:
        none
    return:
        错误数
    """
    # 设置测试数据的的一个比例（训练数据集比例=1-hoRatio）
    hoRatio = 0.1  # 测试范围,一部分测试一部分作为样本
    # 从文件中加载数据
    datingDataMat, datingLabels = file2matrix('input/2.KNN/datingTestSet2.txt')  # load data setfrom file
    # 归一化数据
    normMat, ranges, minVals = autoNorm(datingDataMat)
    # m 表示数据的行数，即矩阵的第一维
    m = normMat.shape[0]
    # 设置测试的样本数量， numTestVecs:m表示训练样本的数量
    numTestVecs = int(m * hoRatio)
    print 'numTestVecs=', numTestVecs
    errorCount = 0.0
    for i in range(numTestVecs):
        # 对数据测试
        classifierResult = classify0(normMat[i, :], normMat[numTestVecs:m, :], datingLabels[numTestVecs:m], 3)
        print "the classifier came back with: %d, the real answer is: %d" % (classifierResult, datingLabels[i])
        if (classifierResult != datingLabels[i]): errorCount += 1.0
    print "the total error rate is: %f" % (errorCount / float(numTestVecs))
    print errorCount

def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    #距离度量 度量公式为欧氏距离
    diffMat = tile(inX, (dataSetSize,1)) – dataSet
    sqDiffMat = diffMat**2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances**0.5
    
    #将距离排序：从小到大
    sortedDistIndicies = distances.argsort()
    #选取前K个最短距离， 选取这K个中最多的分类类别
    classCount={}
    for i in range(k)：
        voteIlabel = labels[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1 
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]
"""
    训练算法：此步骤不适用于 k-近邻算法

    因为测试数据每一次都要与全量的训练数据进行比较，所以这个过程是没有必要的。
    
    """














