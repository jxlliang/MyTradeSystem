# -*- coding:utf-8 -*- 
"""
__author_email="1013359736@qq.com"
#Author: Jxl
"""
import sys,os
sys.path.append('..')
from Resource.EnumType import *
from Resource.Common import *
from BaseStrategy import *

class DoubleRsi(Strategys):
    author = u'小鸡快跑'
    strategyName = 'DoubleRsi'
    update = '2017-11-06'
    parameter ={'code1':'IH1711','code2':'IC1712','tradeCount':'1','tradeTime':'09:30-15:00','max_tradeNum':'230','max_CapitalNum':'1000000','tradeCount_Ratio':'1:2','spread_Ratio':'1:3'}
    def __init__(self,eventEngine,common):
        super(DoubleRsi,self).__init__(eventEngine,common)
        self.__eventEngine=eventEngine
        self.__common=common

    def startStrategy(self):
        """策略开始"""
        pass
    def onPositionData(self):
        pass

    def onAccountData(self):
        pass

    def onRtnOrder(self,event):
        pass

    def onRtnTrade(self,event):
        pass

    def onMarketData(self,event):
        """行情到达"""
        print 'event==',event.dict['']

    def endStrategy(self):
        """策略结束"""
        pass