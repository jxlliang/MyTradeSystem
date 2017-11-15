# coding:utf-8
"""
author=fenglelanya
learn more

"""
"""Common 对底层API进行一层简化的封装，方便用户的调用"""
from CentralEngine import *
from eventType import *
from EnumType import *
from CTP_Api import *
from collections import OrderedDict
import datetime
from EM_Finance_apis import *

class Common(object):
    def __init__(self):
        super(Common,self).__init__()
        self.engine=EventEngine()
        self.engine.start() #  启动引擎
        self.enumQuoteApiType=EnumQuoteApiType
        self.enumTradeApiType=EnumTradeApiType
        self.getCount=0
        self.index_count=0
        self.td_apisDict=OrderedDict() # 启动了的API类型（key=account,value=API_Type)
        self.md_apisDict=OrderedDict()
        self.dictInstrument={} ## 字典（保存合约查询数据）
        self.account_AptType=OrderedDict()  # 账号对应的API类型
        self.tdapiClassDict={} # 把交易API名称和该API的实例做一个映射（通过交易API名称直接调用API的实例）
        self.mdapiClassDict={} # 把行情API名称和该API的实例做一个映射


    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.engine.put(event)

    def md_Login(self,address,userid, password, brokerid,api_type=None):  #, userid, password, brokerid
        """行情账号登录"""
        ctpapi_=self.enumQuoteApiType.CTP_Future_Md.name
        guoxinFixapi_=self.enumQuoteApiType.Fix_GuoXin_Stock_Md.name
        em_Finance=self.enumQuoteApiType.EM_DongFang_Finance_Md.name
        if api_type==ctpapi_:
            self.ctp_quoteApi=ctpMdApi(self.engine)
            self.md_apisDict[ctpapi_]=self.ctp_quoteApi
            IP=address.encode('utf-8')
            userID=userid.encode('utf-8')
            pwd=password.encode('utf-8')
            brokerID=brokerid.encode('utf-8')
            self.ctp_quoteApi.login(IP,userID,pwd,brokerID)
            self.mdapiClassDict[api_type]=self.ctp_quoteApi

        elif api_type==guoxinFixapi_:
            #self.md_apisDict[guoxinFixapi_]=self.
            #self.mdapiClassDict[api_type] = self.
            print u'fix行情API'

        elif api_type==em_Finance:
            #self.md_apisDict[em_Finance]=self.
            self.EM_md_api = EM_Finance_Quote_Api(self.engine)
            self.EM_md_api.login(userid, password, address, brokerid)
            self.engine.register(EVENT_INDEX_MARKETDATA, self.initGetEMStock)
            self.mdapiClassDict[api_type]=self.EM_md_api

    def td_Login(self,address,userid, password, brokerid,api_type=None):  #self, address, userid, password, brokerid):
        """行情账号登录"""
        ctpapi_=self.enumTradeApiType.CTP_Future_Td.name
        guoxinFixapi_=self.enumTradeApiType.Fix_GuoXin_Stock_Td.name

        if api_type==ctpapi_:
            self.ctp_tradeApi=ctpTdApi(self.engine)
            self.td_apisDict[ctpapi_]=self.ctp_tradeApi
            IP=address.encode('utf-8')
            userID=userid.encode('utf-8')
            pwd=password.encode('utf-8')
            brokerID=brokerid.encode('utf-8')
            self.ctp_tradeApi.login(IP,userID,pwd,brokerID)
            self.tdapiClassDict[api_type]=self.ctp_tradeApi # 把ctp的API名称和ctp API的实例做映射
            self.engine.register(EVENT_TDLOGIN,self.initGet)
            self.engine.register(EVENT_INSTRUMENT,self.insertInstrument)

        elif api_type==guoxinFixapi_:
            #self.md_apisDict[guoxinFixapi_]=self.
            #self.tdapiClassDict[api_type]=self.  # 把国信fix API名称和fix接口的实例做映射
            print u'fix行情API'


    def subscribe(self, instrumentid, exchangeid,api_type=None):
        """订阅合约"""
        if api_type in self.mdapiClassDict:
            self.mdapiClassDict[api_type].subMarketData(instrumentid,exchangeid)

    def sendOrder(self, instrumentid, exchangeid, price, volume, direction, offset,api_type=None):
        """发单"""
        DirectionDict = {}
        DirectionDict[EnumDirectionType.Buy.name] = '0'
        DirectionDict[EnumDirectionType.Sell.name] =  '1'

        OffsetFlagDict = {}
        OffsetFlagDict[EnumOffsetFlagType.Open.name] = '0'
        OffsetFlagDict[EnumOffsetFlagType.Close.name] = '1'
        OffsetFlagDict[EnumOffsetFlagType.ForceClose.name] = '2'
        OffsetFlagDict[EnumOffsetFlagType.CloseToday.name] = '3'
        OffsetFlagDict[EnumOffsetFlagType.CloseYesterday.name] = '4'
        OffsetFlagDict[EnumOffsetFlagType.ForceOff.name] = '5'
        OffsetFlagDict[EnumOffsetFlagType.LocalForceClose.name] = '6'

        if api_type in self.tdapiClassDict:
            orderRef=self.tdapiClassDict[api_type].orderInsert(instrumentid,exchangeid,price,volume,DirectionDict[direction],OffsetFlagDict[offset])
            return orderRef

    def cancelOrder(self, instrumentid, exchangeid, orderref, frontid, sessionid,api_type=None):
        """撤单"""
        if api_type in self.tdapiClassDict:
            self.tdapiClassDict[api_type].orderCancel(instrumentid,exchangeid,orderref,frontid,sessionid)

    #++++++++++++++++++++++++++针对东方财富的接口获取指数数据+++++++++++++++++++++++++++++++++++++++++++++++++
    def round_Stockdata(self,event):
        """从接口中获取股票数据"""
        self.index_count+=1
        if self.index_count>=3: #3s更新一次行情
            self.index_count=0
            self.EM_md_api.code_List()

    def initGetEMStock(self,event):
        """循环通过新浪/腾讯/东财的接口获取股票数据"""
        #self.EM_md_api.subscribeData()
        self.engine.register(EVENT_TIMER,self.round_Stockdata)

    # ++++++++++++++++++++++++++针对东方财富的接口获取指数数据+++++++++++++++++++++++++++++++++++++++++++++++++
    def getInstrumentMarginRate(self,code,api_type=None):
        """获取合约的保证金率"""
        if api_type in self.td_apisDict:
            self.td_apisDict[api_type].getInstrumentMarginRate(code)

    def getInstrument(self):
        """获取合约(统一获取所有已登录的交易账号对应的交易所的合约)"""
        {api_class.getInstrument() for api_name, api_class in self.td_apisDict.items()}

    def getInvestor(self):
        """查询投资者(统一获取所有已登录的交易账号对应的交易所的投资者)"""
        #log=u'查询投资者'
        #self.log(log)
        {api_class.getInvestor() for api_name, api_class in self.td_apisDict.items()}

    def getPosition(self):
        """查询持仓(统一获取所有已登录的交易账号对应的持仓)"""
        #log=u'查询持仓'
        #self.log(log)
        { api_class.getPosition() for api_name,api_class in self.td_apisDict.items() }

    def getAccount(self):
        """查询账户信息(统一获取所有已登录的交易账号对应的账号信息)"""
        log=u'查询账户信息'
        #self.log(log)
        {api_class.getAccount() for api_name, api_class in self.td_apisDict.items()}

    def getAccountPosition(self, event):
        """循环查询账户和持仓"""
        self.getCount += 1

        # 每5秒发一次查询
        if self.getCount ==10:
            self.getPosition()
        elif self.getCount==20:
            self.getCount = 0
            self.getAccount()

    # ----------------------------------------------------------------------
    def initGet(self, event):
        """在交易服务器登录成功后，开始初始化查询"""
        # 打开设定文件setting.vn
        f = shelve.open('Instrument.vn')
        # 尝试读取设定字典，若该字典不存在，则发出查询请求
        try:
            d = f['instrument']
            # 如果本地保存的合约数据是今日的，则载入，否则发出查询请求
            today = date.today()
            if d['date'] == today:
                self.dictInstrument = d['dictInstrument']
                log = u'合约信息读取完成'
                self.log(log)
                self.getInvestor()
                # 开始循环查询
                self.ee.register(EVENT_TIMER, self.getAccountPosition)

            else:
                self.getInstrument()
        except KeyError:
            self.getInstrument()

        f.close()

    def insertInstrument(self, event):
        """插入合约对象"""
        data=event.dict_['data']
        last=event.dict_['last']
        self.dictInstrument[data['InstrumentID']]=data
        # 合约对象查询完成后，查询投资者信息并开始循环查询
        if last:
            # 将查询完成的合约信息保存到本地文件，今日登录可直接使用不再查询
            #print u'合约查询完全！！！'
            self.saveInstrument()
            self.log(u'合约信息查询完成')
            self.getInvestor() # 查询投资者
            self.engine.register(EVENT_TIMER,self.getAccountPosition)

    def saveInstrument(self):
        """保存合约到本地"""
        instrumentData=shelve.open('setting.vn')
        data={}
        data['dictInstrument']=self.dictInstrument
        data['date'] =datetime.datetime.today()
        instrumentData['instrument'] = data
        instrumentData.close()

    def exit(self):
        """销毁指定的API"""
        for api_name,api_clase in self.apisDict.items():
            api_clase.exit()
        self.engine.stop() # 停止事件引擎
        print u'销毁指定的API'



