# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 07:05:12 2018

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

def candle_plot(code,num=22,start_index=0):
    
    hist = pd.read_csv('D:/vn.py/vnpy-1.7.1/securities_analysis/data/'+code+'_D.csv')
    hist.index = hist.iloc[:,0]
    hist=hist.iloc[::-1]
    hist.index = pd.to_datetime(hist.index,format='%Y-%m-%d')
    hist = hist.iloc[:,1:]
    #candleplot(hist)

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
    '''
    mondays = WeekdayLocator(MONDAY)
    weekformatter = DateFormatter('%y %b %d')
    ax.xaxis.set_major_formatter(weekformatter)
    
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_major_locator(DayLocator())
    
    '''    
    candlestick_ohlc(ax,listData,width=0.5, \
                      colorup ='r',colordown='g')
    
    #ax.set_title(title)
    return(plt)
#复权数据蜡烛图********************************************************************************************    
def candle_plot1(code,num,start_index):
    
    hist = pd.read_csv('D:/vn.py/vnpy-1.7.1/securities_analysis/data/'+code+'_qfq.csv')
    hist.index = hist.iloc[:,1]
    #hist=hist.iloc[::-1]
    hist.index = pd.to_datetime(hist.index,format='%Y-%m-%d')
    hist = hist.iloc[:,2:]
    #candleplot(hist)

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
    '''
    mondays = WeekdayLocator(MONDAY)
    weekformatter = DateFormatter('%y %b %d')
    ax.xaxis.set_major_formatter(weekformatter)
    
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_major_locator(DayLocator())
    
    '''    
    candlestick_ohlc(ax,listData,width=0.5, \
                      colorup ='r',colordown='g')
    
    #ax.set_title(title)
    return(plt)

#fig = candle_plot('601336')
#fig.savefig('D:/vn.py/vnpy-1.7.1/securities_analysis/data/601336_'+'.png')
#连续蜡烛图********************************************************************************************
def candle_plot2(code,num=22):
    
    hist = pd.read_csv('C:/Users/Administrator/stockPriditionProjects/data/'+code+'.csv')
    hist.index = hist.iloc[:,0]
    hist=hist.iloc[::-1]
    hist.index = pd.to_datetime(hist.index,format='%Y-%m-%d')
    hist = hist.iloc[:,1:]
    #candleplot(hist)
    
    for i in range(len(hist)-num):
        print("step"+str(i)+"*"*20)
        seriesdata = hist.iloc[i:i+22]
    
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
        '''
        mondays = WeekdayLocator(MONDAY)
        weekformatter = DateFormatter('%y %b %d')
        ax.xaxis.set_major_formatter(weekformatter)
        
        ax.xaxis.set_major_locator(mondays)
        ax.xaxis.set_major_locator(DayLocator())
        
        '''    
        candlestick_ohlc(ax,listData,width=0.5, \
                          colorup ='r',colordown='g')
        
        #ax.set_title(title)
        plt.savefig('D:/hellodata/candleplot/601336_'+str(i)+'.jpg')
    
    return(plt.show())
    
#在线数据绘制蜡烛图********************************************************************************************   
def candle_plot3(code,num=22):    
    hist_data = ts.get_hist_data('601558')
    # 对tushare获取到的数据转换成candlestick_ohlc()方法可读取的格式
    data_list = []
    for dates,row in hist_data.iterrows():
        # 将时间转换为数字
        date_time = datetime.datetime.strptime(dates,'%Y-%m-%d')
        t = date2num(date_time)
        Open,high,close,low = row[:4]
        datas = (t,Open,high,low,close)
        data_list.append(datas)
    
    data_list = data_list[:20]
    # 创建子图
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    # 设置X轴刻度为日期时间
    ax.xaxis_date()
    plt.xticks(rotation=45)
    plt.yticks()
    plt.title("股票代码：601558两年K线图")
    plt.xlabel("时间")
    plt.ylabel("股价（元）")
    mpf.candlestick_ohlc(ax,data_list,width=0.5,colorup='r',colordown='g')
    plt.grid()
    plt.show()
    plt.savefig('C:/Users/Administrator/stockPriditionProjects/data/601558_k_line.jpg')

if __name__ == '__main__':
    plt.show()
    plt.savefig('C:/Users/Administrator/stockPriditionProjects/data/601558_k_line.jpg')
