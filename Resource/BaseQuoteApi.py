# coding:utf-8
"""
author=fenglelanya
learn more

"""
from EnumType import *
from CentralEngine import *

class BaseQuoteApi(object):

    def __init__(self,eventEngine):
        super(BaseQuoteApi,self).__init__()
        self.baseEventEngine=eventEngine
        self.baseEnumQuoteApiType=EnumQuoteApiType
        # 请求编号，由api负责管理
        self.baseReqid = 0
        # 以下变量用于实现连接和重连后的自动登陆
        self.baseUser = ''
        self.basePwd = ''
        self.baseBrokeId = ''
        # 以下集合用于重连后自动订阅之前已订阅的合约，使用集合为了防止重复
        self.baseSetSubscribed = set()


    # ================================主动函数==============================↓↓↓↓↓↓
    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.baseEventEngine.put(event)

    def connect(self):
        """行情API连接"""
        pass

    def disConnect(self):
        """"""
        pass

    def login(self, address, userid, password, brokerid):
        """行情账号登录"""
        pass

    def subMarketData(self, instrumentid, exchangeid):
        """订阅行情"""
        pass

    def unSubMarketData(self,instrumentid):
        """退订行情"""
        pass

    def exit_Api(self):
        """安全退出API"""
        pass
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++↑↑↑↑↑↑



    #================================回调函数==============================↓↓↓↓↓↓
    def onFrontConnected(self):
        """行情API登录回报"""
        pass

    def onFrontDisconnected(self,n):
        """行情API登出回报"""
        pass

    def onRtnDepthMarketData(self,data):
        """行情数据推送"""
        pass

    def onRspUnSubMarketData(self,data):
        """退订行情"""
        pass

    def onRspError(self, error, n, last):
        """错误回报"""
        pass

    def onRspUserLogin(self, data, error, n, last):
        """行情账号登录回报"""
        pass

    def onRspUserLogout(self,data, error, n, last):
        """行情账号登出回报"""
        pass

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++↑↑↑↑↑↑