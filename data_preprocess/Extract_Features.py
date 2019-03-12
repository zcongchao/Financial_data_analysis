# -*- coding: utf-8 -*-
import datetime as dt
from datetime import timedelta
import numpy as np
import pandas as pd
import os
from snownlp import SnowNLP
from lunar import Lunar

path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/'

class Extract_Features:
    '''
    # 提取特征
    # classifier's features X:
          weekday:[1:7]
          lunar_month:[1:12]
          season:[1:4]
          comment's sentiment: SnowNLP, based on short text classifier's result
          economical environment : cpi, gdp_year, gdp_quarter,  money_supply
    # label Y: actual trends
          0: increase
        #? 1: keep
          2: decrease
    '''

    def __init__(self):
        pass
    
    #计算上下行波动率因子*************************************************************
    def duvol(self,code):
        '''
        :param code:股票代码
        :returnfactor_vol_data: 上下行波动率
        '''
        hist_data = pd.read_csv(path + code + '_qfq.csv')
        hist_data.index = hist_data['date']
        
        hist_data['daily_return'] = np.log(hist_data['close']/hist_data['close'].shift(1))
        hist_data['three_month_mean'] = pd.rolling_mean(hist_data['daily_return'],60)
        
        daily_return = hist_data['daily_return']
        three_month_mean =  hist_data['three_month_mean']
        
        up_vol_data = pd.DataFrame()
        for i in range(len(daily_return)-120):
            temp1 = daily_return[60+i:120+i]
            temp2 = three_month_mean[60+i:120+i]
            I_i = temp1 > temp2
            up_temp = (((temp1-temp2)*(temp1-temp2))[I_i]).mean()
            temp = {"vol_data":up_temp}
            temp = pd.DataFrame(temp,[temp1.index[-1]])
            #temp.index = [temp1.index[-1]]
            #temp.index = [temp1.index[-1]]
            up_vol_data = up_vol_data.append(temp)
        
        down_vol_data = pd.DataFrame()
        for i in range(len(daily_return)-120):
            temp1 = daily_return[60+i:120+i]
            temp2 = three_month_mean[60+i:120+i]
            I_i = temp1 < temp2
            down_temp = (((temp1-temp2)*(temp1-temp2))[I_i]).mean()
            temp = {"vol_data":down_temp}
            temp = pd.DataFrame(temp,[temp1.index[-1]])
            #temp.index = [temp1.index[-1]]           
            down_vol_data = down_vol_data.append(temp)
        
        factor_vol_data = down_vol_data/up_vol_data
        factor_vol_data = np.log(factor_vol_data)
        return factor_vol_data
    
    #将日期转化为星期*****************************************************************
    def parse_weekday(self, date):
        '''
        :param date:date
        :return: weekday
        '''
        if type(date) is str:
            date = dt.datetime.strptime(date, '%Y-%m-%d')
            return date.isoweekday()
        elif type(date) is dt.date or type(date) is dt.datetime:
            return date.isoweekday()
        else:
            raise TypeError('date must be datetime type!')
            
    #转化为阴历月份*****************************************************************
    def lunar_month(self, date):
        '''
        :param date:date
        :return: lunar month
        '''
        #date = str(date.year)+'-'+str(date.month)+'-'+str(date.day)
        date = dt.datetime.strptime(date, '%Y-%m-%d')
        ln = Lunar(date)
        lunar_date = ln.ln_date()
        return lunar_date[1]
        
    #返回季节*****************************************************************
    def season(self, date):
        '''
        :param date:date
        :return: season
        '''
        dict = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
        if type(date) is dt.datetime or type(date) is dt.date:
            return dict[date.month]
        elif type(date) is str:
            return dict[int(date.split('-')[1])]
            
    #CPI****************************************************************************
    def cpi(self, date):
        '''

        :param date: date
        :return: cpi
        '''
        data = open(path + 'cpi.csv', 'rb').readlines()[1:]
        cpi = {}
        for line in data:
            item = line.split(',')
            cpi_dates = '-'.join(item[1].split('.'))
            cpi_datas = float(item[2])
            cpi[cpi_dates] = cpi_datas

        if type(date) is dt.datetime or type(date) is dt.date:
            return cpi[str(date.year)+"-"+str(date.month)]
        elif type(date) is str:
            return cpi[date.split('-')[0]+'-'+str(int(date.split('-')[1]))]
            
    #price_chage********************************************************************************
    def get_price_chage(self, date):
        '''

        :param date: date
        :return: delta price
        '''
        #date = dt.datetime.strptime(date, '%Y-%m-%d')
        data = pd.read_csv(path + 'sh.csv', index_col='date')
        delta = data['price_change']
        #return delta[str(date.year)+'-'+str(date.month)+'-'+str(date.day)]
        return delta[date]
        
    #sz_close_price********************************************************************************
    def get_sz_close_price(self, date):
        '''
        :param date:
        :return:shenzhen close price
        '''
        data = pd.read_csv(path + 'sh.csv', index_col='date')
        delta = data['close']
        #return delta[str(date.year)+'-'+str(date.month)+'-'+str(date.day)]
        return delta[date]
        
    #年度GDP********************************************************************************
    def gdp_year(self, date):
        data = pd.read_csv(path + 'gdp_year.csv', index_col='year')
        gdp_year_data = data['gdp']
        if type(date) is dt.datetime or type(date) is dt.date:
            return gdp_year_data[date.year]
        elif type(date) is str:
            return gdp_year_data[int(date.split('-')[0])]
        else:
            raise TypeError("type of date must be string or datetime.date or datetime.datetime!")
            
    #季度GDP**************************************************************************************
    def gdp_quarter(self, date):
        data = pd.read_csv(path + 'gdp_quarter.csv', index_col='quarter')
        gdp_year_data = data['gdp']
        if type(date) is dt.date or type(date) is dt.datetime:
            date_for_quarter = date.year + self.season(date)/10.0
            return gdp_year_data[date_for_quarter]
        elif type(date) is str:
            return gdp_year_data[int(date.split('-')[0]) + self.season(date)/10.0]
        else:
            raise TypeError("type of date must be string or datetime.date or datetime.datetime!")
            
    #存款准备金率P**************************************************************************************
    def rrr(self, date):
        data = pd.read_csv(path + 'rrr.csv', index_col='date')
        rrr_data = data['now']
        rrr_data.index = pd.to_datetime(rrr_data.index)
        # date compare...
        if type(date) is str:
            date = dt.datetime.strptime(date, '%Y-%m-%d')
        return rrr_data.loc[rrr_data.index < date][0]
        
    #货币供应量*************************************************************************************
    def MoneySupply(self, date):
        # return last month's data
        data = open(path + 'money_supply.csv', 'rb').readlines()[1:]
        money_supply = {}
        for line in data:
            item = line.split(',')
            money_supply_dates = '-'.join(item[1].split('.'))
            if item[2] == '--':
                continue
            money_supply[money_supply_dates] = float(item[2])

        if type(date) is dt.datetime or type(date) is dt.date:
            if date.month > 1:
                return money_supply[str(date.year) + "-" + str(date.month-1)]
            elif date.month == 1:
                return money_supply[str(date.year-1) + "-" + str(12)]
            else:
                raise "date.month error!"

        elif type(date) is str:
            if int(date.split('-')[1]) > 1:
                if str(date.split('-')[0]) + '-' + str(int(date.split('-')[1])-1) in money_supply.keys():
                    return money_supply[str(date.split('-')[0]) + '-' + str(int(date.split('-')[1])-1)]
                else:
                    if int(date.split('-')[1]) > 2:
                        return money_supply[str(date.split('-')[0]) + '-' + str(int(date.split('-')[1]) - 2)]
                    if int(date.split('-')[1]) == 1:
                        return money_supply[str(int(date.split('-')[0]) - 1) + '-12']
            elif int(date.split('-')[1]) == 1:
                return money_supply[str(int(date.split('-')[0])-1) + '-12']
            else:
                raise "date.month error!"
   
   #提取文本情感特征*****************************************************************
    def short_text_classification(self, date):
        # no used
        print date
        from snownlp import SnowNLP
        # TODO:throw into init()
        with open(path + 'news.txt', 'rb') as f:
            data = []
            data = f.readlines()
            print type(data)

        corpus = []
        item = []
        for i in range(1, len(data) - 1):
            if (i - 1) % 5 == 0:
                continue
            elif (i - 1) % 5 == 1:
                item.append(data[i].rstrip())
            elif (i - 1) % 5 == 2:
                item.append(data[i].rstrip())
            elif (i - 1) % 5 == 3:
                item.append(data[i].rstrip())
            elif (i - 1) % 5 == 4:
                # print item
                corpus.append(item)
                item = []
                continue

        average_sentiment = 0
        sum_sentiment = 0
        temp_date = ""
        count = 1
        summary_dict = {}
        summary_flag = False
        # TODO!
        for i in range(0, len(corpus)):
            # sentiment analysis,result is not very well
            s = SnowNLP(corpus[i][1].decode('utf-8'))
            sentiment = s.sentiments
            # one to many mapping
            summary_dict.setdefault(corpus[i][0], []).append(sentiment)
            # print s.sentiments,":",corpus[i][0],corpus[i][1]
        for key in summary_dict:
            print key, ":",
            for i in summary_dict[key]:
                print i,
            print ''
            
    #构建特征*****************************************************************************************
    def class_feature(self, date):
        feature = []
        feature.append(self.parse_weekday(date))
        feature.append(self.lunar_month(date))
        feature.append(self.season(date))
        feature.append(self.short_text_classification(date))
        return feature
        
    #识别趋势*****************************************************************************************
    def trends(self, code, date):
        if type(date) is str:
            date = dt.datetime.strptime(date, '%Y-%m-%d')
        data = pd.read_csv(path + str(code)+'.csv', index_col='date')
        close_price_trend = data['close']
        subday = date+timedelta(days=-1)
        print type(close_price_trend), subday.year, subday.month, subday.day
        today = close_price_trend[str(date.year)+'-'+str(date.month)+'-'+str(date.day)]
        while str(subday.year)+'-'+str(subday.month)+'-'+str(subday.day) not in close_price_trend.index:
            subday = subday + timedelta(days=-1)

        yesterday = close_price_trend[str(subday.year)+'-'+str(subday.month)+'-'+str(subday.day)]

        if today > yesterday:
            return 1
        else:
            return 0

    def ML_XY(self):
        # TODO, no use
        X_temp = self.class_feature(None)
        X = []
        y = []
        return np.array(X), np.array(y)

    def classification(feature):
        # TODO, no use
        label = None
        return label
