# coding:utf-8
"""
author=fenglelanya
learn more

"""

from BaseQuoteApi import *
from BaseTradeApi import *
from CentralEngine import *
from winctpmd import MdApi
from vnctptd import TdApi
from ctp_data_type import *
import os,sys,time,datetime
sys.path.append('..')

class ctpMdApi(BaseQuoteApi,MdApi):
    """行情API"""
    def __init__(self,eventEngine):
        super(ctpMdApi,self).__init__(eventEngine)
        self.__eventEngine=self.baseEventEngine
        self.__enumQuoteApiType=self.baseEnumQuoteApiType
        self.__reqid=self.baseReqid
        self.__userid=self.baseUser
        self.__pwd=self.basePwd
        self.__brokerid=self.baseBrokeId
        self.__setSubscribed=self.baseSetSubscribed
        # 初始化.con文件的保存目录为\mdconnection，注意这个目录必须已存在，否则会报错
        self.createFtdcMdApi(os.getcwd() + '\\mdconnection\\')

    def login(self, address, userid, password, brokerid):
        """登录行情账号"""
        print u'开始登陆行情API'
        self.__address=address
        self.__userid=userid
        self.__pwd=password
        self.__brokerid=brokerid
        # 注册服务器地址
        self.registerFront(address)   # API底层的实现-->交易所 self.registerFront
        self.init()  # API底层的初始化实现-->交易所

    def subMarketData(self, instrumentid, exchangeid):
        """订阅行情"""
        self.subscribeMarketData(instrumentid)
        instrument = (instrumentid, exchangeid)
        self.__setSubscribed.add(instrument)

    def exit_Api(self):
        """安全退出行情API"""
        self.exit() # 调用底层API封装的退出API函数

    def onFrontConnected(self):
        """行情API登录回报"""
        self.log(u'CTP行情API登录成功')
        # 如果用户已经填入了用户名等等，则自动尝试连接
        if self.__userid:
            req = {}
            req['UserID'] = self.__userid
            req['Password'] = self.__pwd
            req['BrokerID'] = self.__brokerid
            self.__reqid = self.__reqid + 1
            self.reqUserLogin(req, self.__reqid)

    def onFrontDisconnected(self,n):
        """服务器断开"""
        log=u'CTP Api服务器断开'
        self.log(log)

    def onRspUserLogin(self, data, error, n, last):
        """行情账号登录回报"""
        if error['ErrorID']==0:
            log=u'CTP行情账号登录成功'
        else:
            log=u'CTP行情账号登陆回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)

    def onRspUserLogout(self,data, error, n, last):
        """行情账号登出回报"""
        if error['ErrorID']==0:
            log=u'CTP行情账号登录成功'
        else:
            log=u'CTP行情账号登陆回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)

    def onRtnDepthMarketData(self,data):
        """行情回报"""
        event=Event(type_=EVENT_MARKETDATA)
        event.dict_['data']=data
        self.__eventEngine.put(event)

    def onRspUnSubMarketData(self,data):
        """退订行情"""
        log=u'退订行情'
        self.log(log)

    def onRspError(self, error, n, last):
        """错误回报"""
        log = u'CTP行情账号错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)


class ctpTdApi(BaseTradeApi,TdApi):
    """交易API的实现"""
    def __init__(self,eventEngine):
        super(ctpTdApi,self).__init__(eventEngine)
        self.__eventEngine=self.baseEventEngine
        self.enumTradeApiType=self.baseEnumTradeApiType
        self.__userid=self.baseUserid
        self.__pwd=self.basePassword
        self.__brokerid=self.baseBrokerid
        self.__reqid=self.baseReqid
        self.__orderref=self.baseOrderref
        self.__dictInstrument=self.baseDictInstrument
        # 初始化.con文件的保存目录为\tdconnection
        self.createFtdcTraderApi(os.getcwd() + '\\tdconnection\\')

    def login(self, address, userid, password, brokerid):
        """交易账号登录"""
        self.__userid=userid
        self.__pwd=password
        self.__brokerid=brokerid

        # 数据重传模式设为从本日开始
        self.subscribePrivateTopic(0)
        self.subscribePublicTopic(0)
        # 注册服务器地址
        #ip=address.encode('utf-8')
        self.registerFront(address)
        # 初始化连接，成功会调用onFrontConnected
        self.init()

    def getSettlement(self):
        """CTP查询结算信息"""
        today=datetime.datetime.today().strftime('%Y-%m-%d')
        with open(r'config/SettlementInfoConfirm.txt','r') as f:
            date=f.read()
            if today==date:
                self.log(u'CTP今天已经确认过结算信息，请不要重复确认！')
                event = Event(type_=EVENT_TDLOGIN)
                self.__eventEngine.put(event)
            else:
                self.__reqid+=1
                req={}
                req['BrokerID']=self.__brokerid
                req['InvestorID']=self.__userid
                self.reqQrySettlementInfo(req,self.__reqid)

    def confirmSettlement(self):
        """确认结算"""
        self.__reqid+=1
        req={}
        req['BrokerID']=self.__brokerid
        req['InvestorID']=self.__userid
        self.reqSettlementInfoConfirm(req,self.__reqid)

    def getInstrument(self):
        """查询合约"""
        self.__reqid += 1
        req={}
        self.reqQryInstrument(req, self.__reqid) # ReqQryInstrument

    def getInvestor(self):
        """查询投资者"""
        self.__reqid+=1
        req={}
        self.reqQryInvestor(req,self.__reqid)

    def getPosition(self,instrument=None):
        """查询持仓"""
        self.__reqid+=1
        req={}
        req['BrokerID'] = self.__brokerid
        req['InvestorID'] = self.__userid
        if instrument!=None:
            req['InstrumentID'] = instrument
        requesID=self.reqQryInvestorPosition(req,self.__reqid)

    def getAccount(self):
        """查询账号"""
        self.__reqid+=1
        req={}
        requesID=self.reqQryTradingAccount(req,self.__reqid)
        print u'账号查询返回的requesID==',requesID

    def getInstrumentMarginRate(self,code):
        """查询合约保证金率"""
        self.__reqid+=1
        req={}
        req['InstrumentID']=code
        self.reqQryInstrumentMarginRate(req,self.__reqid)

    def orderInsert(self, instrumentid, exchangeid, price, volume, direction, offset):
        """下单指令"""
        self.__reqid+=1
        req={}
        req['InstrumentID'] = instrumentid
        req['LimitPrice'] = price
        req['VolumeTotalOriginal'] = volume
        req['Direction'] = direction
        req['CombOffsetFlag'] = offset
        req['ExchangeID']=exchangeid
        self.__orderref += 1
        req['OrderRef'] = str(self.__orderref)

        req['InvestorID'] = self.__userid
        req['UserID'] = self.__userid
        req['BrokerID'] = self.__brokerid

        req['OrderPriceType'] = defineDict["THOST_FTDC_OPT_LimitPrice"] # 限价
        req['CombHedgeFlag'] = defineDict['THOST_FTDC_HF_Speculation']  # 投机单
        req['ContingentCondition'] = defineDict['THOST_FTDC_CC_Immediately']  # 立即发单
        req['ForceCloseReason'] = defineDict['THOST_FTDC_FCC_NotForceClose']  # 非强平
        req['IsAutoSuspend'] = 0  # 非自动挂起
        req['TimeCondition'] = defineDict['THOST_FTDC_TC_GFD']  # 今日有效
        req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']  # 任意成交量
        req['MinVolume'] = 1  # 最小成交量为1
        print u'CTP api处下单了--->req==', req
        return self.reqOrderInsert(req, self.__reqid)

    def orderCancel(self, instrumentid, exchangeid, orderref, frontid, sessionid):
        """撤单指令"""
        self.__reqid+=1
        req={}
        req['InstrumentID']=instrumentid
        req['Exchangeid']=exchangeid
        req['OrderRef'] = orderref
        req['FrontID'] = frontid
        req['SessionID'] = sessionid

        req['ActionFlag'] = defineDict['THOST_FTDC_AF_Delete']
        req['BrokerID'] = self.__brokerid
        req['InvestorID'] = self.__userid
        self.reqOrderAction(req, self.__reqid)

    def exit_Api(self):
        """安全退出API"""
        self.exit()

    def onRspUserLogin(self, data, error, n, last):
        """交易账号登录回报"""
        if error['ErrorID']==0:
            log=u'CTP交易账号登录成功'
        else:
            log = u'CTP登陆回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)
        self.getSettlement() # ctp账号登录成功后必须进行结算确认操作

    def onRspUserLogout(self, data, error, n, last):
        """交易账号登出回报"""
        if error['ErrorID']==0:
            log=u'CTP交易账号登出成功'
        else:
            log= u'CTP登出回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)

    def onFrontConnected(self):
        """交易API连接回报"""
        log=u'CTP交易API连接成功'
        self.log(log)
        # 如果用户已经填入了用户名等等，则自动尝试连接
        if self.__userid:
            req = {}
            req['UserID'] = self.__userid
            req['Password'] = self.__pwd
            req['BrokerID'] = self.__brokerid
            self.__reqid = self.__reqid + 1
            self.reqUserLogin(req, self.__reqid)

    def onFrontDisconnected(self,n):
        """交易API连接断开"""
        log=u'CTP交易服务器连接断开'
        self.log(log)

    def onRspQryInstrument(self, data, error, n, last):
        """合约查询回报"""
        if error['ErrorID'] == 0:
            event = Event(type_=EVENT_INSTRUMENT)
            event.dict_['data'] = data
            event.dict_['last'] = last
            self.__eventEngine.put(event)
        else:
            log = u'CTP合约投资者回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            self.log(log)

    def onRspQryInvestor(self, data, error, n, last):
        """查询投资者回报"""
        if error['ErrorID']==0:
            event=Event(type_=EVENT_INVESTOR)
            event.dict_['data']=data
            self.__eventEngine.put(event)
        else:
            log=u'CTP合约投资者回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            self.log(log)

    def onRspQryInvestorPosition(self, data, error, n, last):
        """查询持仓回报"""
        if error['ErrorID']==0:
            event=Event(type_=EVENT_POSITION)  #====================
            DirectionDict = {}
            DirectionDict['2'] = EnumDirectionType.Buy.name
            DirectionDict['3'] = EnumDirectionType.Sell.name
            posidirection_=data['PosiDirection']
            data['PosiDirection']=DirectionDict[posidirection_]
            CombHedgeFlagDict = {}
            CombHedgeFlagDict['2'] = EnumHedgeFlagEnType.Arbitrage.name  # 套利
            CombHedgeFlagDict['3'] = EnumHedgeFlagEnType.Hedge.name  # 套保
            CombHedgeFlagDict['4'] = EnumHedgeFlagEnType.Covered.name  # 备兑
            CombHedgeFlagDict['1'] = EnumHedgeFlagEnType.Speculation.name  # 投机
            posihedgeFlag_=data['HedgeFlag']
            data['HedgeFlag']=CombHedgeFlagDict[posihedgeFlag_]
            PositionDict={}
            PositionDict['1']=EnumPositionDate.Today.name # 今日持仓
            PositionDict['2']=EnumPositionDate.History.name # 历史持仓
            posiDate=data['PositionDate']
            data['PositionDate']=PositionDict[posiDate]

            event.dict_['data']=data  #====================
            self.__eventEngine.put(event)   #====================


        else:
            log=u'CTP持仓查询回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            self.log(log)

    def onRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        print u'资金账户查询回报'
        if error['ErrorID'] == 0:
            event = Event(type_=EVENT_ACCOUNT)
            event.dict_['data'] = data
            self.__eventEngine.put(event)
        else:
            log=u'CTP持仓账户回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            self.log(log)

    def onRspQryInstrumentMarginRate(self,data,error,n,last):
        """查询合约保证金率回报"""
        if error['ErrorID']==0:
            event=Event(type_=EVENT_INSTRUMENTMARGINRATE)
            event.dict_['data']=data
            self.__eventEngine.put(event)
        else:
            log = u'CTP保证金率查询回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            self.log(log)

    def onRspQrySettlementInfo(self, data, error, n, last):
        """查询结算回报"""
        if last:
            log = u'结算信息查询完成'
            self.log(log)
            self.confirmSettlement()  # 查询完成后立即确认结算信息

    def onRspSettlementInfoConfirm(self, data, error, n, last):
        """确认结算回报"""
        log = u'结算信息确认完成'
        self.log(log)
        event = Event(type_=EVENT_TDLOGIN)
        self.__eventEngine.put(event)
        self.getInvestor()
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        with open(r'config/SettlementInfoConfirm.txt','w') as f:
            f.write(today)

    def onRtnOrder(self,data):
        """委托回报"""
        self.onRtnOrder_Trade(data,EVENT_ORDER)

    def onRtnTrade(self,data):
        """成交回报"""
        self.onRtnOrder_Trade(data,EVENT_TRADE)

    def onRtnOrder_Trade(self,data,type_order_trade):
        """order trade公用"""
        newref = data['OrderRef']
        self.__orderref = max(int(newref), self.__orderref)
        if type_order_trade==EVENT_ORDER:
            orderStatusTypeDict={}
            orderStatusTypeDict['0']=EnumOrderStatusType.AllTraded.name
            orderStatusTypeDict['1']=EnumOrderStatusType.NoTradeQueueing.name
            orderStatusTypeDict['2']=EnumOrderStatusType.NoTradeQueueing.name
            orderStatusTypeDict['3']=EnumOrderStatusType.NoTradeQueueing.name
            orderStatusTypeDict['4']=EnumOrderStatusType.NoTradeQueueing.name
            orderStatusTypeDict['5']=EnumOrderStatusType.Canceled.name
            orderStatusTypeDict['a']=EnumOrderStatusType.Unknown.name
            orderStatusTypeDict['b'] =EnumOrderStatusType.NotTouched.name
            orderStatusTypeDict['c'] = EnumOrderStatusType.Touched.name
            statusType=data['OrderStatus']
            data['OrderStatus']=orderStatusTypeDict[statusType]

        CombHedgeFlagDict = {}
        CombHedgeFlagDict['2'] = EnumHedgeFlagEnType.Arbitrage.name  # 套利
        CombHedgeFlagDict['3'] = EnumHedgeFlagEnType.Hedge.name  # 套保
        CombHedgeFlagDict['4'] = EnumHedgeFlagEnType.Covered.name  # 备兑
        CombHedgeFlagDict['1'] = EnumHedgeFlagEnType.Speculation.name  # 投机
        if type_order_trade==EVENT_TRADE:
            hedgeFlagType = data['HedgeFlag']
            print u'交易回报==>套期保值标志==',hedgeFlagType
            data['HedgeFlag'] = CombHedgeFlagDict[hedgeFlagType]
        elif type_order_trade==EVENT_ORDER:
            hedgeFlagType = data['CombHedgeFlag']
            data['CombHedgeFlag'] = CombHedgeFlagDict[hedgeFlagType]

        DirectionDict = {}
        DirectionDict['0'] = EnumDirectionType.Buy.name
        DirectionDict['1'] = EnumDirectionType.Sell.name
        direction = data['Direction']
        data['Direction'] = DirectionDict[direction]

        OffsetFlagDict = {}
        OffsetFlagDict['0'] = EnumOffsetFlagType.Open.name
        OffsetFlagDict['1'] = EnumOffsetFlagType.Close.name
        OffsetFlagDict['2'] = EnumOffsetFlagType.ForceClose.name
        OffsetFlagDict['3'] = EnumOffsetFlagType.CloseToday.name
        OffsetFlagDict['4'] = EnumOffsetFlagType.CloseYesterday.name
        OffsetFlagDict['5'] = EnumOffsetFlagType.ForceOff.name
        OffsetFlagDict['6'] = EnumOffsetFlagType.LocalForceClose.name
        if type_order_trade == EVENT_TRADE:
            offset = data['OffsetFlag']
            data['CombOffsetFlag'] = OffsetFlagDict[offset]
        elif type_order_trade == EVENT_ORDER:
            offset = data['CombOffsetFlag']
            data['CombOffsetFlag'] = OffsetFlagDict[offset]
        event = Event(type_=type_order_trade)
        event.dict_['data'] = data
        self.__eventEngine.put(event)

    def onRspError(self, error, n, last):
        """错误回报"""
        log = u'CTP交易所错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)
        print log

    def onErrRtnOrderAction(self, data, error):
        """撤单失败回报"""
        log=u'CTP撤单错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)

    def onErrRtnOrderInsert(self, data, error):
        """下单失败回报"""
        log=u'CTP发单错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        self.log(log)




