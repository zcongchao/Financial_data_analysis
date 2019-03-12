import tensorflow as tf
import pandas as pd
import numpy as np
from numpy import *

def dnn_mlp(x_train,x_test,y_train,y_test):
    x_train = np.matrix(x_train)
    x_test = np.matrix(x_test)
    y_train = np.matrix(y_train).T
    y_test = np.matrix(y_test).T
    
    n_samles = x_train.shape[0]
    feature_dim = x_train.shape[1]
    
    sess = tf.InteractiveSession()
    
    #输入节点数
    in_units = feature_dim
    #隐含层输出节点数
    h1_units = 300
    #权重，标准差为0.1的截断正态分布,通过truncated_normal来实现,
    #因为模型使用的激活函数是Relu，所以需要使用正态分布参数加一点噪声，打破完全对称和0梯度
    w1 = tf.Variable(tf.truncated_normal([in_units,h1_units],stddev=0.1))
    #偏置初始化为0
    b1 = tf.Variable(tf.zeros([h1_units]))
    #最后输出层的softmax,直接将权重和偏置全部初始化为0即可
    w2 = tf.Variable(tf.zeros([h1_units,1]))
    b2 = tf.Variable(tf.zeros([1]))
    
    x = tf.placeholder(tf.float32,[None,in_units])
    keep_prob = tf.placeholder(tf.float32)
    
    #隐藏层，激活函数为relu
    hidden1 = tf.nn.relu(tf.matmul(x,w1) + b1)
    #Dropout功能，这里的keep_prob参数为保留数据不置为零的数据比例
    hidden1_drop = tf.nn.dropout(hidden1,keep_prob)
    #输出层
    y_ = tf.nn.softmax(tf.matmul(hidden1_drop,w2) + b2)
    
    y = tf.placeholder(tf.float32,[None,1])
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(y*tf.log(y_),reduction_indices=[1]))
    #优化器使用Adagrad,学习速率设为0.3
    train_step = tf.train.AdagradOptimizer(0.3).minimize(cross_entropy)
    
    
    tf.global_variables_initializer().run()
    for i in range(3000):
        #设置keep_prob为0.75，即有25%的数据重置
        train_step.run({x:x_train,y:y_train,keep_prob:0.75})
        
        
    correct_prediction = tf.equal(tf.argmax(y_,1),tf.argmax(y,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
    return accuracy.eval({x:x_test,y:y_test,keep_prob:1.0})