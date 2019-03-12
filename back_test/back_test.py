# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 11:21:37 2018

@author: Administrator
"""
import numpy as np 
import pandas as pd

#信号函数***************************************************************************************
def signal_data(oneDayLine, dates,predicted_Y_test, Y_test):
    hist = predicted_Y_test
    Close = oneDayLine[-(len(hist)+7):]
    Date = dates[-(len(hist)+7):]
    hist_data = {'close':Close}
    hist_data = pd.DataFrame(hist_data)
    hist_data.index = Date
    
    hist ={'Y_predicted':hist}
    hist = pd.DataFrame(hist)
    date = dates[-(len(hist)+7):-7]
    hist.index = date
    
    Y_test = {'Y_test':Y_test}
    Y_test = pd.DataFrame(Y_test)
    print len(Y_test),len(date)

    Y_test.index = date
    
    hist_data = pd.concat([hist_data,hist,Y_test],axis=1)
    
    return hist_data
  
    
#回测函数***************************************************************************************
def back_test(hist_data):
    buy_index = hist_data[hist_data['Y_predicted']>hist_data['Y_test']].index
    
    hist_data.loc[buy_index,'signal'] = 1
    
    true = [1]*len(hist_data['signal'])
    true = {'true':true}
    true = pd.DataFrame(true)
    hist_data = pd.concat([hist_data,true],axis=1)
    
    for i in range(6,len(hist_data)+6):
        sell_Index = hist_data[hist_data['signal'][i-6]==1.0].index
    hist_data.loc[sell_Index,'signal'] = 0
    
    hist_data['keep'] = hist_data['signal']
    hist_data['keep'].fillna(method='ffill',inplace=True)
    
    #计算每天的基准收益,相当于下面的benchmark_profit2
    hist_data['benchmarkProfit'] = \
        np.log(hist_data['close'] / hist_data['close'].shift(1))
    
    #相当于创建了一个滤波器，过滤掉输入信号为0的结果
    hist_data['trendProfit'] = hist_data['keep']*hist_data['benchmarkProfit']
    #最后计算两者的累计收益并可视化对比
    return hist_data[['benchmarkProfit','trendProfit']].cumsum().plot(grid=True,figsize=(14,7))
    
    
"""    
    #度量的基本使用方法
    from abupy import AbuFactorBuyBreak, AbuFactorAtrNStop, AbuFactorPreAtrNStop, AbuFactorCloseAtrNStop
    from abupy import abu, ABuProgress, GridSearch, ABuFileUtil, ABuGridHelper, AbuMetricsBase, AbuBlockProgress
        
    # 设置初始资金数
    read_cash = 1000000
    # 设置选股因子，None为不使用选股因子
    stock_pickers = None
    # 买入因子依然延用向上突破因子
    buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak},
                   {'xd': 42, 'class': AbuFactorBuyBreak}]
    
    # 卖出因子继续使用上一章使用的因子
    sell_factors = [
        {'stop_loss_n': 1.0, 'stop_win_n': 3.0,
         'class': AbuFactorAtrNStop},
        {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.5},
        {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    ]
    # 择时股票池
    choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                      'usTSLA', 'usWUBA', 'usVIPS']
    # 使用run_loop_back运行策略
    abu_result_tuple, kl_pd_manager = abu.run_loop_back(read_cash,
                                                       buy_factors,
                                                       sell_factors,
                                                       stock_pickers,
                                                       choice_symbols=
                                                       choice_symbols,
                                                       n_folds=2)
    ABuProgress.clear_output()
    
    #夏普比率
    def sharpe(rets, ann=252):
        return rets.mean() / rets.std() * np.sqrt(ann)
    
    print('策略sharpe值计算为＝{}'.format(sharpe(metrics.algorithm_returns)))
    """