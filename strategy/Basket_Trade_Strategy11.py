# -*- coding:utf-8 -*- 
"""
__author_email="1013359736@qq.com"
#Author: Jxl
"""
import sys,os
sys.path.append('..')
#from Resource.Common import *
from BaseStrategy import *
from EnumType import *
from Resource.eventType import *
import talib as tb
import numpy as np
from scipy import io as spio


class Basket_Trade(Strategys):
    author = u'不是英雄不扛刀'
    strategyName = 'Basket_Trade'
    update = '2017-11-01'
    parameter = {'code1':'IF1711','code2':'IF1712','tradeCount':1,'tradeTime':'09:30-15:00','max_tradeNum':20,'max_CapitalNum':1000000,'initTicks':40,'spread_Ratio':'1:3','fastPeriod':10,'slowPeriod':30}
    def __init__(self,eventEngine=None,common=None,account_ApiTypeDict=None):
        super(Basket_Trade,self).__init__(eventEngine,common,account_ApiTypeDict)
        self.__eventEngine=eventEngine
        self.__common=common
        self.__account_Api=self.baseAccount_Api
        self.allParams=self.parameter
        self.code1DataDict={}
        self.code2DataDict={}
        self.eachCodePositionDict={}
        self.spreadList=[]  # 价差的List
        self.code1='IC1711'
        self.code2 = 'IC1712'
        self.boolTrade=False
        self.registerEvent()
        #print u'策略层面==>策略参数==', self.allParams
        #print u'self.__account_Api==',self.__account_Api

    def registerEvent(self):
        """注册事件监听"""
        self.__eventEngine.register(EVENT_MARKETDATA, self.onMarketData)
        self.__eventEngine.register(EVENT_ORDER, self.onRtnOrder)
        self.__eventEngine.register(EVENT_TRADE, self.onRtnTrade)
        self.__eventEngine.register(EVENT_POSITION, self.onPositionData)
        self.__eventEngine.register(EVENT_ACCOUNT, self.onAccountData)

    def startStrategy(self):
        """策略开始"""
        self.__common.subscribe(self.code1,EnumExchangeIDType.CFFEX.name,EnumQuoteApiType.CTP_Future_Md.name)
        self.__common.subscribe(self.code2,EnumExchangeIDType.CFFEX.name,EnumQuoteApiType.CTP_Future_Md.name)

    def onAccountData(self,event):
        """查询账号回报"""
        pass

    def onPositionData(self,event):
        """查询持仓回报"""
        position=event.dict_['data']
        #print u'所有持仓========',position
        positionsCode=position[EnumOnRspQryInvestorPosition.InstrumentID.name]
        self.eachCodePositionDict[positionsCode]=position

    def onRtnOrder(self,event):
        print u'RtnOrder==',event.dict_['data']

    def onRtnTrade(self,event):
        print u'RtnTrade==',event.dict_['data']


    def onMarketData(self,event):
        """行情到达"""
        data=event.dict_['data']
        if self.code1==data[EnumMarketDataType.InstrumentID.name]:
            self.code1DataDict[self.code1]=data[EnumMarketDataType.LastPrice.name]
        elif self.code2==data[EnumMarketDataType.InstrumentID.name]:
            self.code2DataDict[self.code2]=data[EnumMarketDataType.LastPrice.name]

        if len(self.code1DataDict)>0 and len(self.code2DataDict)>0:
            priceSpread=self.code1DataDict[self.code1] - self.code2DataDict[self.code2] # 近月-远月
            if len(self.spreadList)>0:
                if self.spreadList[-1]!=priceSpread:
                    self.spreadList.append(priceSpread)
            else:
                self.spreadList.append(priceSpread)
            len_spread=len(self.spreadList)
            print u'len_spread==',len_spread
            if len_spread > int(self.parameter['initTicks']): # tick数量的阀值
                self.spreadList.pop(0) # 移除第一个数据
                #real=RSI(priceSpread,timeperiod=14)
                tickList=np.array(self.spreadList,dtype=np.float)
                fastParam=int(self.parameter['fastPeriod'])
                print u'fastParam=',fastParam
                slowParam=int(self.parameter['slowPeriod'])
                fastSMA=tb.SMA(tickList,fastParam)[-1]
                slowSMA=tb.SMA(tickList,slowParam)[-1]
                #sp.cluster()
                #sp.ndimage()
                print u'fastSMA=',fastSMA
                print u'slowSMA=',slowSMA
                print type(fastSMA),type(slowSMA)
                if fastSMA>slowSMA:
                    if self.boolTrade==False:
                        self.boolTrade=True
                        price=self.code2DataDict[self.code2]
                        exID=(EnumExchangeIDType.CFFEX.name)
                        vol=int(self.parameter['tradeCount'])
                        direction=EnumDirectionType.Sell.name
                        offset=EnumOffsetFlagType.Open.name
                        ctp=EnumTradeApiType.CTP_Future_Td.name
                        print self.code2,exID,price,vol,direction,offset,ctp
                        if self.code1 in self.eachCodePositionDict:
                            get_vol=self.eachCodePositionDict[self.code1]
                            if get_vol>= vol:
                                self.__common.sendOrder(self.code1,exID,price,vol,direction,EnumOffsetFlagType.Close.name,ctp)
                                print u'开始下单啦啦啦'
                            else:
                                self.log(u'无法下单，请检查仓位是否达到下单的要求！')


    def endStrategy(self):
        """策略结束"""
        #停止eventEngine
        #断开API
        #退订合约行情
        pass