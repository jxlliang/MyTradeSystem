# -*- coding:utf-8 -*- 
"""
__author_email="1013359736@qq.com"
#Author: Jxl
"""
"""本aip的行情接口封装是基于东方财富"""

import os,time,shelve
from datetime import date
#from Win_CTP_md import MdApi
#from Win_CTP_td import TdApi
from ctp_data_type import defineDict
from ctp_data_type import typedefDict
from CentralEngine import *
from EnumType import *
import BaseQuoteApi
import BaseTradeApi
import requests as rq
from bs4 import BeautifulSoup as BS
import urllib2
from pyquery import PyQuery as pq


class EM_Finance_Trade_Api(BaseTradeApi.BaseTradeApi):
    """
       交易API封装
       对用户暴露的主动函数包括：
       login 登陆
       getInstrument 查询合约信息
       getAccount 查询账号资金
       getInvestor 查询投资者
       getPosition 查询持仓
       sendOrder 发单
       cancelOrder 撤单
       """
    def __init__(self,eventEngine):
        super(EM_Finance_Trade_Api,self).__init__()
        self.__eventEngine=eventEngine
        # +++++++++++++++继承BaseTradeApi的变量++++++++++++++++++
        self.directionType = EnumDirectionType
        self.exchangeIdType = EnumExchangeIDType
        self.offsetFlagType = EnumOffsetFlagType
        self.tradeApiType = EnumTradeApiType
        self.orderstatusType = EnumOrderStatusType
        # 请求编号，由api负责管理
        self.__reqid = self.reqid_Base
        # 报单编号，由api负责管理
        self.order_ref = self.orderRef_Base
        # 以下变量用于实现连接和重连后的自动登陆
        self.__userid = self.userid_Base
        self.__password = self.password_Base
        self.__brokeid = self.brokeid_Base
        # 合约字典（保存合约查询数据）
        self.__dictInstrument = self.dictInstrument_Base
        self.__instrument_path = self.instrument_file_name_Base
        # +++++++++++++++继承BaseTradeApi的变量++++++++++++++++++

    def login(self, userid, password, brokeid, address):
        pass

    def orderInsert(self,code,exchangeid,offset,direction,price,volume):
        pass


class EM_Finance_Quote_Api(BaseQuoteApi.BaseQuoteApi):

    def __init__(self,eventEngine):
        super(EM_Finance_Quote_Api,self).__init__(eventEngine)
        self.directionIDType = self.baseEnumQuoteApiType

        # 事件引擎，所有数据都推送到其中，再由事件引擎进行分发
        self.__eventEngine = eventEngine
        # 请求编号
        self.__reqid = self.baseReqid
        # 以下变量用于实现连接和重连后的自动登陆
        self.__userid = self.baseUser
        self.__password = self.basePwd
        self.__brokeid = self.baseBrokeId

        self.datadic = {}  #用于存放新浪/腾讯/东财股票接口获取回来的数据
        # 以下集合用于重连后自动订阅之前已订阅的合约，使用集合为了防止重复
        self.__setIndexSubscribed = self.baseSetSubscribed  #指数集合 set()
        self.__setStockSubscribed=self.baseSetSubscribed  #股票集合 set()
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

    def login(self,userid,password,address,brokeid):
        self.code_List()

    def code_List(self):
        """订阅合约list"""
        self.__setIndexSubscribed = ['000001','000300','000905','000016','399006']
        for c in self.__setIndexSubscribed:
            if c[0]=='0':
                self.subscribeData(c, EnumExchangeIDType.SSE.name)
            else:
                self.subscribeData(c, EnumExchangeIDType.SZSE.name)


    def subscribeData(self,instrumentid,exchangeid):
        if exchangeid==EnumExchangeIDType.SSE.name:
           url = r"http://qt.gtimg.cn/q=sh{}".format(instrumentid)
           self.toRtnStockMarket(url,instrumentid)

        elif exchangeid==EnumExchangeIDType.SZSE.name:
            url=r"http://qt.gtimg.cn/q=sz{}".format(instrumentid)
            self.toRtnStockMarket(url,instrumentid)


    def toRtnStockMarket(self,url,instrumentid):
        """"""
        respon = rq.get(url, headers=self.headers).text
        respon_list = respon.split('~')
        if instrumentid in self.__setIndexSubscribed:
            self.onRtnIndexMarketdatas(respon_list)
        elif instrumentid in self.__setStockSubscribed:
            self.onRtnStockMarkedatas(respon_list)

    def onRtnIndexMarketdatas(self,respon_list):
        """指数行情"""
        self.indexDatadic = {}  # 用于存放新浪/腾讯/东财指数接口获取回来的数据
        self.indexDatadic[EnumIndexDataType.Name.name]=respon_list[1]
        self.indexDatadic[EnumIndexDataType.Code.name] = respon_list[2]
        self.indexDatadic[EnumIndexDataType.LastPrice.name] = respon_list[3]
        self.indexDatadic[EnumIndexDataType.PreCloesPrice.name] = respon_list[4]
        self.indexDatadic[EnumIndexDataType.OpenPrice.name] = respon_list[5]
        self.indexDatadic[EnumIndexDataType.Up_Time.name]=respon_list[30][-6:-4]+":"+respon_list[30][-4:-2]+":"+respon_list[30][-2:]
        self.indexDatadic[EnumIndexDataType.ZhangDie_num.name] = respon_list[31]
        self.indexDatadic[EnumIndexDataType.ZhangDie_Rate.name] = respon_list[32]+"%"
        self.indexDatadic[EnumIndexDataType.HightestPrice.name] = respon_list[33]
        self.indexDatadic[EnumIndexDataType.LowestPrice.name] = respon_list[34]
        self.indexDatadic[EnumIndexDataType.Amplitude_Rate.name] = respon_list[43]+"%"
        event_index = Event(type_=EVENT_INDEX_MARKETDATA) # EVENT_INDEX_MARKETDATA
        event_index.dict_['data'] = self.indexDatadic
        self.__eventEngine.put(event_index)

    def onRtnStockMarkedatas(self,respon_list):
        """把从腾讯/新浪/东财接口上获取到的数据存到dict里"""
        self.datadic[EnumStockDataType.Ex_Code.name] = respon_list[0][2:-3]
        self.datadic[EnumStockDataType.Name.name] = respon_list[1]
        self.datadic[EnumStockDataType.Code.name] = respon_list[2]
        self.datadic[EnumStockDataType.LastPrice.name] = respon_list[3]
        self.datadic[EnumStockDataType.PreClosePrice.name] = respon_list[4]
        self.datadic[EnumStockDataType.OpenPrice.name] = respon_list[5]
        self.datadic[EnumStockDataType.Vol_Shou.name] = respon_list[6]
        self.datadic[EnumStockDataType.Out_Pan.name] = respon_list[7]
        self.datadic[EnumStockDataType.In_Pan.name] = respon_list[8]
        self.datadic[EnumStockDataType.Bid1Price.name] = respon_list[9]
        self.datadic[EnumStockDataType.Bid1Vol.name] = respon_list[10]
        self.datadic[EnumStockDataType.Bid2Price.name] = respon_list[11]
        self.datadic[EnumStockDataType.Bid2Vol.name] = respon_list[12]
        self.datadic[EnumStockDataType.Bid3Price.name] = respon_list[13]
        self.datadic[EnumStockDataType.Bid3Vol.name] = respon_list[14]
        self.datadic[EnumStockDataType.Bid4Price.name] = respon_list[15]
        self.datadic[EnumStockDataType.Bid4Vol.name] = respon_list[16]
        self.datadic[EnumStockDataType.Bid5Price.name] = respon_list[17]
        self.datadic[EnumStockDataType.Bid5Vol.name] = respon_list[18]
        self.datadic[EnumStockDataType.Ask1Price.name] = respon_list[19]
        self.datadic[EnumStockDataType.Ask1Vol.name] = respon_list[20]
        self.datadic[EnumStockDataType.Ask2Price.name] = respon_list[21]
        self.datadic[EnumStockDataType.Ask2Vol.name] = respon_list[22]
        self.datadic[EnumStockDataType.Ask3Price.name] = respon_list[23]
        self.datadic[EnumStockDataType.Ask3Vol.name] = respon_list[24]
        self.datadic[EnumStockDataType.Ask4Price.name] = respon_list[25]
        self.datadic[EnumStockDataType.Ask4Vol.name] = respon_list[26]
        self.datadic[EnumStockDataType.Ask5Price.name] = respon_list[27]
        self.datadic[EnumStockDataType.Ask5Vol.name] = respon_list[28]
        self.datadic[EnumStockDataType.Up_time.name] = respon_list[30]
        self.datadic[EnumStockDataType.ZhangDie_num.name] = respon_list[31]
        self.datadic[EnumStockDataType.ZhangDie_Rate.name] = respon_list[32]
        self.datadic[EnumStockDataType.HightPrice.name] = respon_list[33]  # 最高价
        self.datadic[EnumStockDataType.LowPrice.name] = respon_list[34]  # 最低价
        self.datadic[EnumStockDataType.Turnover_Rate.name] = respon_list[38]
        self.datadic[EnumStockDataType.PE.name] = respon_list[39]  # 市盈率
        self.datadic[EnumStockDataType.Amplitude_Rate.name] = respon_list[43]  # 振幅
        self.datadic[EnumStockDataType.Circulation_Market_Value.name] = respon_list[44]
        self.datadic[EnumStockDataType.Market_Capitalization.name] = respon_list[45]
        self.datadic[EnumStockDataType.RaisinglimitPrice.name] = respon_list[47]
        self.datadic[EnumStockDataType.LimitdownPrice.name] = respon_list[48]
        event_stock = Event(type_=EVENT_STOCK_EM_MARKETDATA) # 东方财富股票的行情
        event_stock.dict_['data'] = self.datadic
        self.__eventEngine.put(event_stock)

    def exit_Api(self):
        self.__eventEngine.stop()