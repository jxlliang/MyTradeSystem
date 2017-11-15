# coding:utf-8
"""
author=fenglelanya
learn more
"""
import sys,os
sys.path.append('..')
from Resource.CentralEngine import *
from Resource.Common import *
from Resource.EnumType import *
from Resource.eventType import *

class Strategys(object):
    strategyName=u'' # 策略名称
    author=u''  # 策略创建作者
    update=u'' # 策略创建时间
    parameter={} # 策略的所有参数
    def __init__(self,eventEngine=None,common=None,account_ApiTypeDict=None):
        super(Strategys,self).__init__()
        self.baseEngine=eventEngine
        self.com=common
        self.baseAccount_Api=account_ApiTypeDict
        self.baseEnumQuoteApi=EnumQuoteApiType
        self.baseEnumTradeApi=EnumTradeApiType
        self.baseEnumExchangeID=EnumExchangeIDType
        self.baseEnumOffsetFlag=EnumOffsetFlagType
        self.baseEnumDirection=EnumDirectionType

    def log(self,log):
        #打印log
        event= Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.baseEngine.put(event)
    def getInstrumentMarginRate(self,code,api_type=None):
        """获取合约的保证金率"""
        pass

    def registerEvent(self):
        """监听"""
        pass

    def onAccountData(self,event):
        """账号查询回报"""
        pass

    def onPositionData(self,event):
        """持仓查询回报"""
        pass

    def startStrategy(self):
        """策略启动"""
        pass

    def onMarketData(self,event):
        """行情到达"""
        pass

    def onRtnOrder(self,event):
        '''委托回报'''
        pass

    def onRtnTrade(self,event):
        '''成交回报'''
        pass

    def endStrategy(self):
        '''策略结束'''
        pass
