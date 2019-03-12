# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 15:35:59 2018

@author: Administrator
"""
import pymongo
import json
import tushare as ts
from datetime import timedelta
import datetime 
import time
import numpy as np
from sklearn import preprocessing
import os
import numpy
import errno
import shutil
from candle_plot import candle_plot1

path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/'

#下载历史价格*******************************************************************************************************
def download_to_mongodb(code,ktype ='D',start='2013-01-04'):
    """
    下载股票的行情数据
    :param code:股票代码
    :param ktype:数据周期，默认为日线
    """
    mongo_url = '127.0.0.1:27017'
    client = pymongo.MongoClient(mongo_url)
    database = ktype + '_' + 'data'
    conn = client[database]
    collection = str(code) + '_qfq'
    cursor = conn[collection]
    # 查询数据库中已有数据的最后日期
    cx = cursor.find(sort=[('date',pymongo.DESCENDING)])
    
    if cx.count():
        last = cx[0]
    else:
        last = ''
    #开始下载数据
    if last:
        start = datetime.date(*map(int, str(last['date']).split('-'))) + timedelta(days=1)
        start = str(start)
        
    data = ts.get_k_data(code,start)
    
    if not data.empty:
        # 创建date索引
        cursor.ensure_index([('date',pymongo.ASCENDING)],unique=True)
        cursor.insert(json.loads(data.to_json(orient='records')))
        print '%s下载完成' %code
        
    else:
        print '没有可更新数据%s' %code

#下载财经新闻***********************************************************************
def load_news_from_tushare(top=5,show_content=True):
    new = ts.get_latest_news(top=5,show_content=True)
    f= open(path + 'new_today.txt','wt')
    for i in range(len(new)):
        f.write(str(new.iloc[i]))
    f.close()
    
#下载历史价格***********************************************************************
def download_from_tushare(code,ktype ='D',**kwargs):
    """
    :param code:股票代码
    :param ktype:数据周期，默认为日线
    :**kwargs:其它参数
    """  
    # 1 day line
    hist_data = ts.get_hist_data(code,ktype ='D',**kwargs)
    if hist_data is not None:
        hist_data.to_csv(path+str(code)+'_'+ str(ktype) + '.csv')
        return True
    else:
        return False
    
#下载复权数据***********************************************************************
def download_fq_data_from_tushare(code,years=3,ktype ='D',autype='qfq'):
    '''
    根据历史数据日期请求复盘数据
    :param code:股票代码
    :years:默认为3年
    :ktype:默认为日线
    :autype:复权类型，默认为前复权
    :return:
    '''
    # 取上证最后一天日期做比对，如果个股没有则不存储
    sh_index_lastday = open(path+'sh'+'_'+str(ktype)+'.csv', 'rb').readlines()[1:][0]
    start = datetime.datetime.today().date() + datetime.timedelta(-365 * years)
    fp_data = ts.get_k_data(code,ktype ='D',autype='qfq',start=str(start))
    
    if fp_data is not None and len(fp_data) > 1 and \
    fp_data['date'].tolist()[-1] == sh_index_lastday.split(',')[0]:
        
        fp_data.to_csv(path + str(code) + '_' + str(autype) + '.csv')
        return True
    else:
        return False

#宏观经济指标********************************************************************************************
def download_economy():
    
    #货币供应量
    ts.get_money_supply().to_csv(path+'money_supply.csv')
    #季度GDP
    ts.get_gdp_quarter().to_csv(path+'gdp_quarter.csv')
    #年度GDP
    ts.get_gdp_year().to_csv(path + 'gdp_year.csv')
    #CPI
    ts.get_cpi().to_csv(path+'cpi.csv')
    
    #存款准备金率
    ts.get_rrr().to_csv(path + 'rrr.csv')
    
#加载历史数据********************************************************************************
def load_from_mongodb(code,ktype ='D',start='2013-01-04'):
    mongo_url = '127.0.0.1:27017'
    client = pymongo.MongoClient(mongo_url)
    database = ktype + '_' + 'data'
    conn = client[database]
    collection = str(code) + '_qfq'
    cursor = conn[collection]
    
    queryArgs = {}
    projectionFields = {'close':True,'date':True,'_id':False}
    data = cursor.find(queryArgs,projectionFields)
    close = []
    date = []
    for d in data:
        d_close = d['close']
        d_date = d['date']
        close.append(d_close)
        date.append(d_date)
    return close,date
    
#加载本地数据********************************************************************************************   
def load_data(path):
    '''
    load data from quandl
    :return:close_price,dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_close_data = []
    raw_open_data = []
    raw_dates = []
    for line in f:
        try:
            close_price = float(line.split(',')[3])
            raw_close_data.append(close_price)

            open_price = float(line.split(',')[1])
            raw_open_data.append(open_price)

            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_open_data, raw_close_data, raw_dates     #inverse order
    
#加载本地复权数据********************************************************************************************   
def load_q_data(path):
    '''
    load data from quandl
    :return:close_price,dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_close_data = []
    raw_open_data = []
    raw_dates = []
    for line in f:
        try:
            close_price = float(line.split(',')[3])
            raw_close_data.append(close_price)

            open_price = float(line.split(',')[2])
            raw_open_data.append(open_price)

            raw_dates.append(line.split(',')[1])
        except:
            continue
    return raw_open_data, raw_close_data, raw_dates     #inverse order

#加载开盘价******************************************************************************************** 
def load_open_price(path):
    '''
    load data from quandl
    :return:open_price,dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            open_price = float(line.split(',')[1])
            raw_data.append(open_price)
            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_data[::-1], raw_dates[::-1]     #inverse order
#加载收盘价******************************************************************************************** 
def load_data_from_tushare(path):
    '''
    load data from tushare
    :return:close_price,dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            close_price = float(line.split(',')[3])
            raw_data.append(close_price)
            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_data[::-1], raw_dates[::-1]  # inverse order
    
#加载均价和均量********************************************************************************************
def load_open_close_volume_ma5_vma5_turnover_from_tushare(path):
    '''
    load data from tushare
    :return:ma5,vma5,dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_open_price = []
    raw_close_price = []
    raw_volume = []
    raw_ma5 = []
    raw_vma5 = []
    raw_turnover = []
    raw_dates = []
    for line in f:
        try:
            open_price = float(line.split(',')[1])
            raw_open_price.append(open_price)

            close_price = float(line.split(',')[3])
            raw_close_price.append(close_price)

            volume = float(line.split(',')[5])
            raw_volume.append(volume)

            ma5 = float(line.split(',')[8])
            raw_ma5.append(ma5)

            vma5 = float(line.split(',')[11])
            raw_vma5.append(vma5)

            turnover = float(line.split(',')[14])
            raw_turnover.append(turnover)

            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_open_price[::-1], raw_close_price[::-1], raw_volume[::-1], raw_ma5[::-1], raw_vma5[::-1], raw_turnover[::-1], raw_dates[::-1]  # inverse order

#加载复权的均价和均量********************************************************************************************
def load_fq_open_close_volume_ma5_vma5_turnover_from_tushare(path):
    '''
    load fq data from tushare
    :return:ma5,vma5,dates
    '''
    fq_f = open(path, 'rb').readlines()[1:]
    filepath = os.path.split(path)
    prefix_filename = os.path.splitext(filepath[1])
    fn = prefix_filename[0].split('_')[0]

    f = open(os.path.join(filepath[0], fn)+'.csv', 'rb').readlines()[1:]
    fdates = [d.split(',')[0] for d in f]
    raw_open_price = []
    raw_close_price = []
    raw_volume = []
    raw_ma5 = []
    raw_vma5 = []
    raw_turnover = []
    raw_dates = []
    last_outstanding = 0.0
    for i, fq_line in enumerate(fq_f):
        try:

            open_price = float(fq_line.split(',')[2])
            raw_open_price.append(open_price)

            close_price = float(fq_line.split(',')[3])
            raw_close_price.append(close_price)

            volume = float(fq_line.split(',')[6])
            raw_volume.append(volume)

            if i < 5:
                line5_temp = fq_f[:i + 1]
            else:
                line5_temp = fq_f[i - 5 +1:i+1]

            ma5_temp = [float(m.split(',')[3]) for m in line5_temp]
            raw_ma5.append(numpy.mean(ma5_temp))

            vma5_temp = [float(m.split(',')[6]) for m in line5_temp]
            raw_vma5.append(numpy.mean(vma5_temp))

            if fq_line.split(',')[1] in fdates:
                date_index = fdates.index(fq_line.split(',')[1])
                line = f[date_index]
                turnover = float(line.split(',')[14])
            else:
                if last_outstanding == 0.0:
                    turnover = 0.6
                else:
                    turnover = volume / last_outstanding


            raw_turnover.append(turnover)
            if turnover == 0.0:
                turnover = 1
            last_outstanding = volume / turnover

            raw_dates.append(fq_line.split(',')[1])
        except Exception as e:
            print ('load_fq error : ',e)
            continue
    # return raw_open_price[::-1], raw_close_price[::-1], raw_volume[::-1], raw_ma5[::-1], raw_vma5[::-1], raw_dates[::-1] # inverse order
    return raw_open_price, raw_close_price, raw_volume, \
        raw_ma5, raw_vma5, raw_turnover, raw_dates
    # return raw_open_price[5:], raw_close_price[5:], raw_volume[5:], raw_ma5[5:], raw_vma5[5:], raw_dates[5:]

#加载不同周期的均价********************************************************************************************
def load_fq_ma5_ma10_ma20_ma30_ma60_ma120_ma250_ma500_from_tushare(code):
    '''
    load fq data from tushare
    :return:ma5_ma10_ma20_ma30_ma60_ma120_ma250_ma500_,dates
    '''
    # if os.path.exists('./data/stock_data/'+str(code)+'.csv'):
    f = open(path + str(code)+'.csv', 'rb').readlines()[1:]
    fdates = [d.split(',')[0] for d in f]
    fq_f = open(path + str(code)+'_qfq.csv', 'rb').readlines()[1:]
    raw_open_price = []
    raw_close_price = []
    raw_volume = []
    raw_ma5 = []
    raw_vma5 = []
    raw_turnover = []

    raw_ma10 = []
    raw_ma20 = []
    raw_ma30 = []
    raw_ma60 = []
    raw_ma120 = []
    raw_ma250 = []
    raw_ma500 = []
    raw_ma_order = []
    raw_dates = []
    for fq_line in fq_f:
        try:
            date_index = fdates.index(fq_line.split(',')[1])
            line = f[date_index]

            # open_price = float(line.split(',')[1])
            open_price = float(fq_line.split(',')[2])
            raw_open_price.append(open_price)

            # close_price = float(line.split(',')[3])
            close_price = float(fq_line.split(',')[3])
            raw_close_price.append(close_price)

            volume = float(fq_line.split(',')[6])
            raw_volume.append(volume)


            ma5_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line)+5]
            ma5_temp = [float(m.split(',')[3]) for m in ma5_temp]
            # numpy.mean(ma5_temp)
            raw_ma5.append(numpy.mean(ma5_temp))

            ma10_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line)+10]
            ma10_temp = [float(m.split(',')[3]) for m in ma10_temp]
            raw_ma10.append(numpy.mean(ma10_temp))

            ma20_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line)+20]
            ma20_temp = [float(m.split(',')[3]) for m in ma20_temp]
            raw_ma20.append(numpy.mean(ma20_temp))

            ma30_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line)+30]
            ma30_temp = [float(m.split(',')[3]) for m in ma30_temp]
            raw_ma30.append(numpy.mean(ma30_temp))

            ma60_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line)+60]
            ma60_temp = [float(m.split(',')[3]) for m in ma60_temp]
            raw_ma60.append(numpy.mean(ma60_temp))

            ma120_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line) + 120]
            ma120_temp = [float(m.split(',')[3]) for m in ma120_temp]
            raw_ma120.append(numpy.mean(ma120_temp))

            ma250_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line) + 250]
            ma250_temp = [float(m.split(',')[3]) for m in ma250_temp]
            raw_ma250.append(numpy.mean(ma250_temp))

            ma500_temp = fq_f[fq_f.index(fq_line):fq_f.index(fq_line) + 500]
            ma500_temp = [float(m.split(',')[3]) for m in ma500_temp]
            raw_ma500.append(numpy.mean(ma500_temp))

            if numpy.mean(ma5_temp)<numpy.mean(ma10_temp)<numpy.mean(ma20_temp)< \
                numpy.mean(ma30_temp)<numpy.mean(ma60_temp)<numpy.mean(ma120_temp)< \
                numpy.mean(ma250_temp)<numpy.mean(ma500_temp):
                # print 'code',str(code),  fq_line.split(',')[0]
                raw_ma_order.append(1)
            else:
                raw_ma_order.append(0)

            # vma5 = float(line.split(',')[11])
            # raw_vma5.append(vma5)

            turnover = float(line.split(',')[14])
            raw_turnover.append(turnover)

            raw_dates.append(fq_line.split(',')[1])
        except:
            continue
    return raw_close_price[::-1], raw_ma5[::-1], raw_ma10[::-1], raw_ma20[::-1], \
        raw_ma30[::-1], raw_ma60[::-1], raw_ma120[::-1], raw_ma250[::-1], \
        raw_ma500[::-1], raw_ma_order[::-1], raw_turnover[::-1], raw_dates[::-1]  # inverse order
    # else:
    #     return
#加载不同周期的均均量********************************************************************************************
def load_index_open_close_volume_ma5_vma5_from_tushare(path):
    '''
    load index data from tushare
    :return:ma5,vma5,dates
    '''
    f = open(path, 'rb').readlines()[1:]
    # fq_f = open(path, 'rb').readlines()[1:]
    raw_open_price = []
    raw_close_price = []
    raw_volume = []
    raw_ma5 = []
    raw_vma5 = []
    raw_dates = []
    for i, line in enumerate(f):
        try:
            # index, date, open, close, high, low, volume, code
            open_price = float(line.split(',')[2])
            raw_open_price.append(open_price)

            close_price = float(line.split(',')[3])
            raw_close_price.append(close_price)

            volume = float(line.split(',')[6])
            raw_volume.append(volume)

            if i < 5:
                line5_temp = f[:i + 1]
            else:
                line5_temp = f[i - 5+1:i+1]

            ma5_temp = [float(m.split(',')[3]) for m in line5_temp]
            raw_ma5.append(numpy.mean(ma5_temp))

            vma5_temp = [float(m.split(',')[6]) for m in line5_temp]
            raw_vma5.append(numpy.mean(vma5_temp))


            raw_dates.append(line.split(',')[1])
        except:
            continue
    # return raw_open_price[::-1], raw_close_price[::-1], raw_volume[::-1], raw_ma5[::-1], raw_vma5[::-1], raw_dates[::-1]  # inverse order
    return raw_open_price, raw_close_price, raw_volume, raw_ma5, raw_vma5, raw_dates
    # return raw_open_price[5:], raw_close_price[5:], raw_volume[5:], raw_ma5[5:], raw_vma5[5:], raw_dates[5:]


#加载成交量********************************************************************************************
def load_volume_from_tushare(path):
    '''
    load data from tushare
    :return:volume, dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            close_price = float(line.split(',')[5])
            raw_data.append(close_price)
            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_data[::-1], raw_dates[::-1]  # inverse order

#加载所有数据********************************************************************************************
def load_all_items_from_tushare(path):
    '''
    load data from tushare
    :return:open,high,close,low,volume,price_change,p_change,ma5,ma10,ma20,v_ma5,v_ma10,v_ma20,turnover;dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            raw_data.append(line.split(',')[1:])
            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_data[::-1], raw_dates[::-1]  # inverse order
    
#加载常用数据********************************************************************************************
def load_all_item_from_tushare(path):
    '''
    load data from tushare
    :return:open,high,close,low; dates
    '''
    f = open(path, 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            raw_data.append(line.split(',')[1:5])
            raw_dates.append(line.split(',')[0])
        except:
            continue
    return raw_data[::-1], raw_dates[::-1]  # inverse order
    
#大单交易数据********************************************************************************************
def get_big_deal_volume(code, date, volume = 400):
    '''
    :param code:
    :param date:
    :param volume:
    :return:
    '''
    # 大单交易数据 取所有大单的差值
    big_deals = ts.get_sina_dd(str(code), date=date, vol=volume)
    if big_deals is None:
        big_deals = 0
    else:
        lines = big_deals.T.to_dict()

        big_volume = 0
        for key, line in lines.items():
            if (line['type']) == "卖盘":
                big_volume -= float(line['volume'])
            elif (line['type']) == "买盘":
                big_volume += float(line['volume'])
        big_deals = big_volume
    return big_deals/1000000
    
#分割数据集********************************************************************************************
def split_into_chunks(data, train, predict, step, binary=True, scale=True):
    X, Y = [], []
    for i in range(0, len(data), step):
        try:
            x_i = data[i:i + train]
            y_i = data[i + train + predict]

            # Use it only for daily return time series
            if binary:
                if y_i > 0.:
                    y_i = [1., 0.]
                else:
                    y_i = [0., 1.]

                if scale: x_i = preprocessing.scale(x_i)

            else:
                timeseries = np.array(data[i:i + train + predict])
                if scale: timeseries = preprocessing.scale(timeseries)
                x_i = timeseries[:-1]
                y_i = timeseries[-1]

        except:
            break

        X.append(x_i)
        Y.append(y_i)

    return X, Y


def create_Xt_Yt(X, y, percentage=0.8,retain = 0):
    '''
    将数据集划分出训练集和测试集,可以设置retain_testset=22留出22天一个月的数据进行测试
    :param X:
    :param y:
    :param percentage: 分割比例
    :return:
    '''

    # retain_testset = 0
    # retain_testset = 22

    X_train = X[0:int(len(X) * percentage)-int(retain*percentage)]
    Y_train = y[0:int(len(y) * percentage)-int(retain*percentage)]

    #若用LSTM做预测,不能洗牌
    #X_train, Y_train = shuffle_in_unison(X_train, Y_train)

    if retain == 0:
        X_test = X[int(len(X) * percentage):]
        Y_test = y[int(len(y) * percentage):]
    else:
        X_test = X[int(len(X) * percentage)-int(retain*percentage):-retain]
        Y_test = y[int(len(y) * percentage)-int(retain*percentage):-retain]



    return X_train, X_test, Y_train, Y_test
    
#用于LSTM模型的数据********************************************************************************************   
def To_DL_datatype(code):
    '''
    :param code: 股票代码
    :return: X,y
    '''
    dayline, date = load_from_mongodb(code,ktype ='D')
    thirtydayline, dates = load_from_mongodb(code,ktype ='M')
    X = []
    y = []
    for i in range(0, len(dayline) - 8):
        dat = date[i].split('-')
        for j, word in enumerate(dates):
            #startswith() 方法用于检查字符串是否是以指定子字符串开头
            if word.startswith(dat[0]+'-'+dat[1]):
                index = j
        X.append(dayline[i:i+7]+thirtydayline[index-12:index])
        y.append(dayline[i+7])
    return np.array(X), np.array(y)

    
#洗牌函数********************************************************************************************
def shuffle_in_unison(a, b):
    
    assert len(a) == len(b)
    a = np.array(a)
    b = np.array(b)
    shuffled_a = np.empty(a.shape, dtype=a.dtype)
    shuffled_b = np.empty(b.shape, dtype=b.dtype)
    permutation = np.random.permutation(len(a))
    for old_index, new_index in enumerate(permutation):
        shuffled_a[new_index] = a[old_index]
        shuffled_b[new_index] = b[old_index]
    return shuffled_a, shuffled_b
    

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

#蜡烛图数据集**********************************************************************************************
def plot_Kline_imgs_for_X(code,days):
    data_path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/'
    stock_path = os.path.join(data_path, code) + '_qfq.csv'
    stockFile = open(stock_path, 'rb').readlines()[1:]
    up_percent = 0.015
    #
    png_dir =path+ 'K_img/%s/' % code
    png_dir_up = png_dir +'up/'
    png_dir_down = png_dir + 'down/'
    #
    if os.path.isdir(png_dir_up) is not True:
        mkdir_p(png_dir_up)
    if os.path.isdir(png_dir_down) is not True:
        mkdir_p(png_dir_down)

    #days-1 因为序号起始从0开始，所以要-1
    for i, line in enumerate(stockFile[days-1:-3]):
        print "step"+str(i)+'/'+str(len(stockFile)-i-1)+"*"*20
        if (days + i + 3) >= len(stockFile):
            break
        ind = i+days
        today_close_price = float(stockFile[ind].split(',')[3])
        nextday_close_price = float(stockFile[ind+1].split(',')[3])
        next2day_close_price = float(stockFile[ind+2].split(',')[3])
        next3day_close_price = float(stockFile[ind+3].split(',')[3])
        up_rule1 = (nextday_close_price - today_close_price)/today_close_price > up_percent
        up_rule2 = (nextday_close_price - today_close_price) > 0 \
                    and (next2day_close_price - nextday_close_price) > 0 \
                    and (next3day_close_price - next2day_close_price) > 0 \
                    and (next3day_close_price - today_close_price) / today_close_price > up_percent*3

        down_rule1 = (nextday_close_price - today_close_price) / today_close_price <= -up_percent
        down_rule2 = (next3day_close_price - today_close_price) / today_close_price <= -up_percent*2
        
        start_index=stockFile.index(line)+1
        #start = time.time()
        if up_rule1 or up_rule2:
            # 放入上涨文件夹
            fig = candle_plot1(code, days, start_index)
            png_path = os.path.join(png_dir_up, code) + '_' + line.split(',')[1] + '.jpg'
            fig.savefig(png_path,  bbox_inches = 'tight', pad_inches = 0)  # facecolor=fig.get_facecolor(),
        elif down_rule1 or down_rule2:
            # 放入下跌
            fig = candle_plot1(code, days, start_index)
            png_path = os.path.join(png_dir_down, code) + '_' + line.split(',')[1] + '.jpg'
            fig.savefig(png_path, bbox_inches = 'tight', pad_inches = 0)

        # print 'time is ', time.time() - start
#划分train和val 集合****************************************************************************************
def prepare_Kline_imgs_for_X(code):
    
    #data_path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/'
    #stock_path = os.path.join(data_path, code) + '_qfq.csv'
    #stockFile = open(stock_path, 'rb').readlines()[1:]
   #up_percent = 0.015
    #
    png_dir =path+ 'K_img/%s/' % code
    png_dir_up = png_dir +'up/'
    png_dir_down = png_dir + 'down/'
    retain_testset = 0
    # retain_testset = 22
    percentage = 0.8
    #
    png_dir_train_up = png_dir +'train/up/'
    png_dir_validation_up = png_dir +'validation/up/'
    png_dir_train_down = png_dir +'train/down/'
    png_dir_validation_down = png_dir +'validation/down/'
    #
    #
    if os.path.isdir(png_dir_train_up) is not True:
        mkdir_p(png_dir_train_up)
    if os.path.isdir(png_dir_validation_up) is not True:
        mkdir_p(png_dir_validation_up)
    if os.path.isdir(png_dir_train_down) is not True:
        mkdir_p(png_dir_train_down)
    if os.path.isdir(png_dir_validation_down) is not True:
        mkdir_p(png_dir_validation_down)



    # 保证上涨和下跌训练集配比1：1，复制上涨到图形一次
    for i, file in enumerate(os.listdir(png_dir_up)):

        downfiles = os.listdir(png_dir_down)
        if len(os.listdir(png_dir_up)) < len(os.listdir(png_dir_down)):
            png_path = os.path.join(png_dir_up, file)
            shutil.copy(png_path, png_path[0:-4] + '_copy.jpg')
        elif len(os.listdir(png_dir_up)) > len(os.listdir(png_dir_down)):
            png_path = os.path.join(png_dir_down, downfiles[i])
            shutil.copy(png_path, png_path[0:-4] + '_copy.jpg')
        else:
            break

    
    up_files = os.listdir(png_dir_up)
    down_files = os.listdir(png_dir_down)

    up_train = up_files[0:int(len(up_files) * percentage)-retain_testset]
    down_train = down_files[0:int(len(down_files) * percentage) - retain_testset]

    if retain_testset == 0:
        up_val = up_files[int(len(up_files) * percentage):]
        down_val = down_files[int(len(down_files) * percentage):]
    else:
        up_val = up_files[int(len(up_files) * percentage)-retain_testset:-retain_testset]
        down_val = down_files[int(len(down_files) * percentage)-retain_testset:-retain_testset]


    for filename in up_train:
        source = os.path.join(png_dir_up, filename)
        target = os.path.join(png_dir_train_up, filename)
        shutil.move(source, target)

    for filename in down_train:
        source = os.path.join(png_dir_down, filename)
        target = os.path.join(png_dir_train_down, filename)
        shutil.move(source, target)

    for filename in up_val:
        source = os.path.join(png_dir_up, filename)
        target = os.path.join(png_dir_validation_up, filename)
        shutil.move(source, target)

    for filename in down_val:
        source = os.path.join(png_dir_down, filename)
        target = os.path.join(png_dir_validation_down, filename)
        shutil.move(source, target)

    shutil.rmtree(png_dir_up)
    shutil.rmtree(png_dir_down)
    print 'complete %s img prepare!' % code



if __name__ == '__main__':
    prepare_Kline_imgs_for_X('600004',10)