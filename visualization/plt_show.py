# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 15:35:59 2018

@author: Administrator
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter,WeekdayLocator, \
DayLocator,MONDAY,date2num
from matplotlib.finance import candlestick_ohlc
import tushare as ts
import datetime
import matplotlib.finance as mpf

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

#用于二维数据可视化比较******************************************************************************************** 
def plt_show(x,y1,y2):
    """
    :param x:x轴时间序列
    :param y1,y2: y轴时间序列
    :return plt.show():二维数据图
    """
    plt.figure(1)
    plt.plot(x[len(x)-len(y1):len(x)], y1, color='g')
    plt.plot(x[len(x)-len(y2):len(x)], y2, color='r')
    return plt.show()
    
#蜡烛图********************************************************************************************    
def candle_plot1(code,num,start_index):
    
    hist = pd.read_csv('D:/vn.py/vnpy-1.7.1/securities_analysis/data/'+code+'_qfq.csv')
    hist.index = hist.iloc[:,1]
   
    hist.index = pd.to_datetime(hist.index,format='%Y-%m-%d')
    hist = hist.iloc[:,2:]
   
    seriesdata = hist.iloc[start_index:start_index+num]

    Date = [date2num(date) for date in seriesdata.index]
    seriesdata.loc[:,'Date'] = Date
           
    listData = []
    for j in range(len(seriesdata)):
        a= [seriesdata.Date[j], \
            seriesdata.open[j],seriesdata.high[j], \
            seriesdata.low[j],seriesdata.close[j]]
        listData.append(a)
          
    ax = plt.subplot()
    ax.xaxis_date()
    plt.xticks(rotation=45)
    candlestick_ohlc(ax,listData,width=0.5, \
                      colorup ='r',colordown='g')
    return(plt)
    
#曲线图******************************************************************************************** 
def plot_line(x,y):
    
    plt.plot(x,y)
    plt.grid(True)
    
#柱状图********************************************************************************************
def plot_hist(y,bins=25):
    plt.figure(figsize=(7,4))
    plt.hist(y,bins=25)
    
#散点图********************************************************************************************
def plot_scatter(y1,y2):
    plt.figure(figsize=(7,5))
    plt.scatter(y1,y2,marker='o')
    plt.grid(True)
    plt.xlabel('1st')
    plt.ylabel('2nd')

#两个子图*******************************************************************************************
def plot_double_line(y1,y2):
    plt.figure(figsize=(7,5))
    plt.subplot(211)
    plt.plot(y1,lw=1.5,label='1st')
    plt.legend(loc=0)
    plt.subplot(212)
    plt.plot(y2,lw=1.5,label='2nd')
    plt.legend(loc=0)