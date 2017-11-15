# coding:utf-8
"""
author=fenglelanya
learn more

"""
from EnumType import *
from CentralEngine import *

class BaseTradeApi(object):

    def __init__(self,eventEngine):
        super(BaseTradeApi,self).__init__()
        self.baseEventEngine=eventEngine
        self.baseEnumTradeApiType=EnumTradeApiType

        # 请求编号，由api负责管理
        self.baseReqid = 0
        # 报单编号，由api负责管理
        self.baseOrderref = 0
        # 以下变量用于实现连接和重连后的自动登陆
        self.baseUserid = ''
        self.basePassword = ''
        self.baseBrokerid = ''
        self.baseOrderref = 0
        # 合约字典（保存合约查询数据）
        self.baseDictInstrument = {}


    # ++++++++++++++++++++主动函数++++++++++++++++++++++++↓↓↓↓↓↓
    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.baseEventEngine.put(event)

    def connect(self):
        """交易API连接"""
        pass

    def disConnect(self):
        """"""
        pass

    def login(self, address, userid, password, brokerid):
        """交易账号登录"""
        pass

    def logout(self):
        """交易账号登出"""
        pass

    def getInstrument(self):
        """查询合约"""
        pass

    def getAccount(self):
        """查询账户"""
        pass

    def getPosition(self,instrument=None):
        """查询持仓"""
        pass

    def getInvestor(self):
        """查询投资者"""
        pass

    def getInstrumentMarginRate(self,code):
        """查询合约的保证金率"""
        pass

    def getSettlement(self):
        """查询结算信息"""
        pass

    def confirmSettlement(self):
        """确认结算信息"""
        pass

    def orderInsert(self, instrumentid, exchangeid, price, volume, direction, offset):
        """下单"""
        pass

    def orderCancel(self, instrumentid, exchangeid, orderref, frontid, sessionid):
        """撤单"""
        pass

    def exit_Api(self):
        """安全退出API"""
        pass
    # ++++++++++++++++++++主动函数++++++++++++++++++++++++↑↑↑↑↑↑




    #++++++++++++++++++++回调函数++++++++++++++++++++++++↓↓↓↓↓↓
    def onFrontConnected(self):
        """交易API连接回报"""
        pass

    def onFrontDisconnected(self,n):
        """交易API断开连接回报"""
        pass

    def onRspUserLogin(self, data, error, n, last):
        """登录回报"""
        pass

    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        pass

    def onRspQryInstrumentMarginRate(self,data,error,n,last):
        """查询合约保证金率回报"""
        pass

    def onRspSettlementInfoConfirm(self, data, error, n, last):
        """确认结算信息回报"""
        pass

    def onRspQryInvestorPosition(self, data, error, n, last):
        """持仓查询回报"""
        pass

    def onRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        pass

    def onRspQryInvestor(self, data, error, n, last):
        """投资者查询回报"""
        pass

    def onRspQryInstrument(self, data, error, n, last):
        """合约查询回报"""
        pass

    def onRspQrySettlementInfo(self, data, error, n, last):
        """查询结算信息回报 OnRspQrySettlementInfo"""
        pass

    def onRspError(self, error, n, last):
        """交易所错误回报"""
        pass

    def onErrRtnOrderInsert(self, data, error):
        """发单错误回报（交易所）"""
        pass

    def onErrRtnOrderAction(self, data, error):
        """撤单错误回报（交易所）"""
        pass

    def onRtnOrder(self,data):
        """委托回报"""
        pass


    def onRtnTrade(self,data):
        """成交回报"""
        pass

    def onRtnOrder_Trade(self,data):
        """供给order和trade公用"""
        pass

    # ++++++++++++++++++++回调函数++++++++++++++++++++++++↑↑↑↑↑↑

class PositionStruct:
    def __init__(self):
        """持仓回报的选定字段"""
        self.InstrumentID=1
        self.BrokerID=2
        self.InvestorID=3
        self.PosiDirection=4
        self.HedgeFlag=5
        self.PositionDate=6
        self.YdPosition=7
        self.Position=8
        self.LongFrozen=9 # 多头冻结
        self.ShortFrozen=10 # 空头冻结
        self.LongFrozenAmount=11 # 多头冻结的金额
        self.ShortFrozenAmount=12 # 空头冻结金额
        self.UseMargin=13 # 占用的保证金
        self.FrozenMargin=14 # 冻结的保证金
        self.FrozenCash=15 # 冻结的资金
        self.FrozenCommission=16 # 冻结的手续费
        self.Commission=17 # 手续费
        self.CloseProfit=18 # 平仓盈亏
        self.PositionProfit=19 # 持仓盈亏
        self.ExchangeID=20 # 交易所的ID
        self.TradingDay=21
