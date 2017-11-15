# encoding: UTF-8
"""
author=fenglelanya
learn more

"""

import os,sys,datetime,time
from PyQt4 import QtGui,QtCore
from Resource.CentralEngine import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from collections import OrderedDict
from Resource.EnumType import *
import configparser

class BaseWidget(QtGui.QTableWidget):
    """各个组件窗体的基类"""
    signal = QtCore.pyqtSignal(type(Event()))
    def __init__(self,eventEngine=None,common=None,parent=None):
        super(BaseWidget,self).__init__(parent)
        self.__engine=eventEngine
        self.__common=common
        self.title=''
        self.columnsDict=OrderedDict()
        self.font = QtGui.QFont(u'微软雅黑', 12)
        self.EVENT_Type = ''
        #self.initMenu()
        #self.initUi(title,columnsDict,self.font)
        #self.registerEvent(EVENT_Type)

    def initUi(self,title,dict,font):
        """"""
        self.setWindowTitle(title)
        self.setColumnCount(len(dict))  #self.setColumnCount(2)
        self.setHorizontalHeaderLabels(dict.values())
        self.setAlternatingRowColors(True) # 隔行改变颜色
        self.verticalHeader().setVisible(False) # # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)  # 设为不可编辑状态
        self.setFont(font)
        self.setSelectionBehavior(QAbstractItemView.SelectRows) # 整行选择

    def rightKeyCsvDatas(self):
        """右键选择把表内数据保存到本地"""

    def registerEvent(self,EVENT_Type):
        """注册事件监听"""
        # Qt图形组件的GUI更新必须使用Signal/Slot机制，否则有可能导致程序崩溃
        # 因此这里先将图形更新函数作为Slot，和信号连接起来,然后将信号的触发函数注册到事件驱动引擎中
        self.signal.connect(self.updateDatas)
        self.__engine.register(EVENT_Type, self.signal.emit)

    def updateDatas(self,event):
        """更新数据"""
        pass

    def saveData(self):
        """保存表格内容到CSV文件"""

        # 获取想要保存的文件名
        path = QtGui.QFileDialog.getSaveFileName(self, '保存数据', '', 'CSV(*.csv)')

        try:
            if not path.isEmpty():
                with open(unicode(path), 'wb') as f:
                    writer = csv.writer(f)

                    # 保存标签
                    headers = [header.encode('gbk') for header in self.headerList]
                    writer.writerow(headers)

                    # 保存每行内容
                    for row in range(self.rowCount()):
                        rowdata = []
                        for column in range(self.columnCount()):
                            item = self.item(row, column)
                            if item is not None:
                                rowdata.append(
                                    unicode(item.text()).encode('gbk'))
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)
        except IOError:
            pass

    # ----------------------------------------------------------------------
    def initMenu(self):
        """初始化右键菜单"""
        self.menu = QtGui.QMenu(self)

        saveAction = QtGui.QAction(u'Save Datas To CSV...', self)
        saveAction.triggered.connect(self.saveData)

        self.menu.addAction(saveAction)

    # ----------------------------------------------------------------------
    def contextMenuEvent(self, event):
        """右键点击事件"""
        self.menu.popup(QtGui.QCursor.pos())

class Log_Data(BaseWidget):
    def __init__(self,eventEngine=None,common=None,colWidth=0,parent=None):
        super(Log_Data,self).__init__(eventEngine,common,parent)
        self.__engine=eventEngine
        self.__common=common
        self.title=u'日志'
        self.columnsDict = OrderedDict()
        self.columnsDict['updateTime']=u'更新时间'  # dictLabels['AccountID'] = u'投资者账户'
        self.columnsDict['updateData']=u'更新日志'
        self.initUi(self.title,self.columnsDict,self.font)
        colWidth0=colWidth/4
        self.setColumnWidth(0, colWidth0)
        self.setColumnWidth(1,colWidth-colWidth0)
        self.EVENT_Type=EVENT_LOG
        self.registerEvent(self.EVENT_Type)
        self.initMenu()


    def rightKeyCsvDatas(self):
        pass

    def updateDatas(self,event):
        """更新日志"""
        # 获取当前时间和日志内容
        t = time.strftime('%H:%M:%S', time.localtime(time.time()))
        log = event.dict_['log']
        #print u'log==',log
        # 在表格最上方插入一行
        self.insertRow(0)
        # 创建单元格
        cellTime = QtGui.QTableWidgetItem(t)
        cellTime.setBackgroundColor(QColor(0, 5, 100))
        cellTime.setTextColor(QColor(100, 200, 100))
        cellTime.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        #textFont = QFont('song', 10, QFont.AllLowercase)
        cellLog = QtGui.QTableWidgetItem(log)
        #cellLog.setFont(textFont)
        cellLog.setBackgroundColor(QColor(0, 5, 100))
        cellLog.setTextColor(QColor(100, 200, 100))
        cellLog.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignLeft)
        # cellTime.setTextAlignment(Qt.AlignCenter)  .setBackgroundRole(QtGui.QPalette.Dark)
        # 将单元格插入表格
        self.setItem(0, 0, cellTime)

        self.setItem(0, 1, cellLog)
        with open(r'config\Wintrade_log.txt', 'a+') as f:
            f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '  ' + log.encode('utf-8') + '\r\n')

class AccountData(BaseWidget):
    def __init__(self,eventEngine=None,common=None,colWidth=0,parent=None):
        super(AccountData,self).__init__(eventEngine,common,parent)
        self.__engine=eventEngine
        self.dictAccount = {}  # 用来保存账户对应的单元格
        self.title=u'账户'
        self.columnsDict=OrderedDict()
        self.columnsDict['AccountID'] = u'投资者账户'
        self.columnsDict['Balance'] = u'账户资金'
        self.columnsDict['WithdrawQuota'] = u'可取资金'
        self.columnsDict['Available'] = u'可用资金'
        self.columnsDict['PositionProfit'] = u'持仓盈亏'
        self.columnsDict['CloseProfit'] = u'平仓盈亏'
        self.columnsDict['Commission'] = u'手续费'
        self.columnsDict['FrozenCash'] = u'冻结资金'
        self.columnsDict['FrozenMargin'] = u'冻结保证金'
        self.initUi(self.title,self.columnsDict,self.font)
        self.EVENT_Type=EVENT_ACCOUNT
        self.registerEvent(self.EVENT_Type)
        self.initMenu()
        eachWidth=colWidth/len(self.columnsDict)
        for col, label in enumerate(self.columnsDict.keys()):
            self.setColumnWidth(col,eachWidth)

    def rightKeyCsvDatas(self):
        pass

    def updateDatas(self,event):
        """U界面上账户信息更新"""
        data = event.dict_['data']
        accountid = data['AccountID']
        # 如果之前已经收到过这个账户的数据, 则直接更新
        if accountid in self.dictAccount:
            d = self.dictAccount[accountid]
            for label, cell in d.items():
                cell.setText(str(data[label]))
        # 否则插入新的一行，并更新
        else:
            self.insertRow(0)
            d = {}
            for col, label in enumerate(self.columnsDict.keys()):
                cell = QtGui.QTableWidgetItem(str(data[label]))
                cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.setItem(0, col, cell)
                d[label] = cell
            self.dictAccount[accountid] = d

class PositionData(BaseWidget):
    def __init__(self,eventEngine=None,common=None,colWidth=0,parent=None):
        super(PositionData,self).__init__(eventEngine,common,parent)
        self.title=u'持仓'
        self.columnsDict=OrderedDict()
        self.engine=eventEngine
        self.columnsDict['InvestorID'] = u'交易账户'
        self.columnsDict['InstrumentID'] = u'合约代码'
        # dictLabels['ExchangeID'] = u'交易所'
        self.columnsDict['PosiDirection'] = u'买卖方向'
        self.columnsDict['Position'] = u'总持仓'
        self.columnsDict['TodayPosition'] = u'今仓'
        self.columnsDict['YdPosition'] = u'昨仓'
        self.columnsDict['PositionProfit'] = u'持仓盈亏'
        # dictLabels['CloseProfit']=u'平仓盈亏'
        self.columnsDict['PositionDate'] = u'持仓日期'
        self.columnsDict['HedgeFlag'] = u'投机/套保'
        self.initUi(self.title,self.columnsDict,self.font)
        self.dictPosition = {}  # 用来保存持仓对应的单元格
        self.EVENT_Type=EVENT_POSITION
        self.registerEvent(self.EVENT_Type)
        self.initMenu()
        #print 'colWidth==',colWidth

        eachWidth=colWidth/len(self.columnsDict)
        for col, label in enumerate(self.columnsDict.keys()):
            self.setColumnWidth(col,eachWidth)

    def rightKeyCsvDatas(self):
        pass

    def updateDatas(self,event):
        """更新合约数据"""
        data = event.dict_['data']
        # 过滤返回值为空的情况
        if data['InstrumentID']:
            posid = data['InstrumentID'] + '.' + data['PosiDirection']
            # 如果之前已经收到过这个账户的数据, 则直接更新
            if posid in self.dictPosition:
                d = self.dictPosition[posid]
                for label, cell in d.items():
                    if data['Position'] == 0:
                        continue
                    value = str(data[label])
                    cell.setText(value)
            # 否则插入新的一行，并更新
            else:
                if data['Position'] > 0:
                    self.insertRow(0)
                    d_0 = {}
                    for col, label in enumerate(self.columnsDict.keys()):
                        value = str(data[label])
                        if data['Position'] == 0:
                            continue
                        cell = QtGui.QTableWidgetItem(value)
                        cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        d_0[label] = cell
                        self.setItem(0, col, cell)
                    self.dictPosition[posid] = d_0

class Trade_Data(BaseWidget):
    def __init__(self,eventEngine=None,common=None,TradeUIWidth=0,parent=None):
        super(Trade_Data,self).__init__(eventEngine,common,parent)
        self.__engine=eventEngine
        self.title=u'成交'
        self.columnsDict=OrderedDict()
        self.columnsDict['TradeID'] = u'成交编号'
        self.columnsDict['InstrumentID'] = u'合约代码'
        self.columnsDict['ExchangeID'] = u'交易所'
        self.columnsDict['Direction'] = u'方向'
        self.columnsDict['OffsetFlag'] = u'开平'
        self.columnsDict['Volume'] = u'数量'
        self.columnsDict['Price'] = u'价格'
        self.columnsDict['TradeTime'] = u'成交时间'
        self.columnsDict['HedgeFlag'] = u'投机/套保'
        self.initUi(self.title,self.columnsDict,self.font)
        self.EVENT_Type=EVENT_TRADE
        self.registerEvent(self.EVENT_Type)
        self.initMenu()
        col_Count=len(self.columnsDict)
        #print '到这里'
        #print col_Count
        #print TradeUIWidth
        eachWidth=TradeUIWidth/col_Count
        #print eachWidth
        for n in range(col_Count):
            self.setColumnWidth(n,eachWidth)


    def rightKeyCsvDatas(self):
        pass

    def updateDatas(self,event):
        data = event.dict_['data']
        self.insertRow(0)
        for col, label in enumerate(self.columnsDict.keys()):
            if label == 'Direction':
                try:
                    value = data[label]
                except KeyError:
                    value = u'未知类型'
            elif label == 'OffsetFlag':
                try:
                    value = data[label]
                except KeyError:
                    value = u'未知类型'
            else:
                value = str(data[label])

            cell = QtGui.QTableWidgetItem(value)
            cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.setItem(0, col, cell)

class Order_Data(BaseWidget):
    signal = pyqtSignal(type(Event()))
    def __init__(self,eventEngine=None,common=None,account_ApiTypeDict=None,colWidth=0,parent=None):
        super(Order_Data,self).__init__(eventEngine,common,parent)
        self.__engine=eventEngine
        self.__common=common
        self.account_apiType = account_ApiTypeDict
        self.dictOrder = {}  # 用来保存报单号对应的单元格对象
        self.dictOrderData = {}  # 用来保存报单数据
        self.title=u'委托'
        self.initMenu()
        self.columnsDict=OrderedDict()
        self.columnsDict['InstrumentID'] = u'合约代码'
        self.columnsDict['ExchangeID'] = u'交易所'
        self.columnsDict['CombOffsetFlag'] = u'开平'
        self.columnsDict['Direction'] = u'方向'
        self.columnsDict['VolumeTotalOriginal'] = u'委托数量'
        self.columnsDict['LimitPrice'] = u'价格'
        self.columnsDict['InsertTime'] = u'委托时间'
        self.columnsDict['VolumeTraded'] = u'成交数量'
        self.columnsDict['OrderStatus'] = u'委托状态'
        self.columnsDict['StatusMsg']=u'状态信息'
        self.initUi(self.title,self.columnsDict,self.font)
        self.EVENT_Type=EVENT_ORDER
        self.registerDatas()
        eachWidth=colWidth/len(self.columnsDict)
        for col, label in enumerate(self.columnsDict.keys()):
            self.setColumnWidth(col,eachWidth)

    def registerDatas(self):
        """监控"""
        self.signal.connect(self.updateDatas)
        self.__engine.register(EVENT_ORDER,self.signal.emit)
        self.itemDoubleClicked.connect(self.cancelOrder)

    def rightKeyCsvDatas(self):
        pass

    def updateDatas(self,event):
        """"""
        data = event.dict_['data']
        orderref = data['OrderRef']
        self.dictOrderData[orderref] = data
        # 如果之前已经收到过这个账户的数据, 则直接更新
        if orderref in self.dictOrder:
            d = self.dictOrder[orderref]
            for label, cell in d.items():
                if label == 'Direction':
                    try:
                        value =data[label]# self.dictDirection[data[label]]
                    except KeyError:
                        value = u'未知类型'
                elif label == 'CombOffsetFlag':
                    try:
                        value =data[label]# self.dictOffset[data[label]]
                    except KeyError:
                        value = u'未知类型'
                elif label == 'StatusMsg':
                    value = data[label].decode('gbk')
                else:
                    value = str(data[label])
                cell.setText(value)

        # 否则插入新的一行，并更新
        else:
            self.insertRow(0)
            d = {}
            for col, label in enumerate(self.columnsDict.keys()):
                if label == 'Direction':
                    try:
                        value = data[label]
                    except KeyError:
                        value = u'未知类型'
                elif label == 'CombOffsetFlag':
                    try:
                        value = data[label]
                    except KeyError:
                        value = u'未知类型'
                elif label == 'StatusMsg':
                    value = data[label].decode('gbk')
                else:
                    value = str(data[label])
                cell = QtGui.QTableWidgetItem(value)
                cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                #cell.setTextAlignment(1)
                self.setItem(0, col, cell)
                d[label] = cell
                cell.orderref =	orderref    # 动态绑定报单号到单元格上
            self.dictOrder[orderref] = d

    def cancelOrder(self, cell):
        """双击撤单"""
        orderref = cell.orderref
        order = self.dictOrderData[orderref]
        # 撤单前检查报单是否已经撤销或者全部成交
        cffex=EnumExchangeIDType.CFFEX.name # 中金所
        czce=EnumExchangeIDType.CZCE.name  #郑商所
        dce=EnumExchangeIDType.DCE.name  #大商所
        shfe=EnumExchangeIDType.SHFE.name  #上期所
        userid=order['UserID']
        api_type = self.account_apiType[userid]  # 调出该账号对应的API类型
        # self, instrumentid, exchangeid, orderref, frontid, sessionid, api_type = None)
        if order['ExchangeID']==cffex or order['ExchangeID']==czce or order['ExchangeID']==dce or order['ExchangeID']==shfe:
            if not (order['OrderStatus'] == '0' or order['OrderStatus'] == '5'):#==0 alltraded   ;  ==5 canceled
                self.__common.cancelOrder(order['InstrumentID'],
                                              order['ExchangeID'],
                                              orderref,
                                              order['FrontID'],#OrderSysID
                                              order['SessionID'],api_type=api_type)

    def cancelAll(self):
        """全撤"""
        for order in self.dictOrderData.values():
            # self, instrumentid, exchangeid, orderref, frontid, sessionid,api_type=None)
            if order['OrderStatus']==EnumOrderStatusType.AllTraded.name or order['OrderStatus']==EnumOrderStatusType.Canceled.name:
                continue
            if not (order['OrderStatus'] == '0' or order['OrderStatus'] == '5'):
                api_type=self.account_apiType[order['UserID']]
                self.__common.cancelOrder(order['InstrumentID'],
                                              order['ExchangeID'],
                                              order['OrderRef'],
                                              order['FrontID'],
                                              order['SessionID'], api_type=api_type)

class Trading(BaseWidget):
    #界面上的交易
    signal_trading=QtCore.pyqtSignal(type(Event()))
    dictDirection=OrderedDict()
    dictDirection['0'] = EnumDirectionType.Buy.name
    dictDirection['1'] = EnumDirectionType.Sell.name
    dictDirection['3'] = EnumDirectionType.ETFPur.name  #ETF申购
    dictDirection['4'] = EnumDirectionType.ETFRed.name  #ETF赎回

    dictOffset=OrderedDict()
    dictOffset['0'] = EnumOffsetFlagType.Open.name
    dictOffset['1'] = EnumOffsetFlagType.Close.name
    dictOffset['2'] = EnumOffsetFlagType.ForceClose.name
    dictOffset['3'] = EnumOffsetFlagType.CloseToday.name      #平今
    dictOffset['4'] = EnumOffsetFlagType.CloseYesterday.name  #平昨

    dictExchangeID = OrderedDict()
    dictExchangeID['J'] = EnumExchangeIDType.CFFEX.name
    dictExchangeID['A'] = EnumExchangeIDType.SSE.name
    dictExchangeID['E'] = EnumExchangeIDType.SZSE.name
    dictExchangeID['N'] = EnumExchangeIDType.INE.name   # 上海能源交易所
    dictExchangeID['D'] = EnumExchangeIDType.DCE.name   # 大商所
    dictExchangeID['Z'] = EnumExchangeIDType.CZCE.name  # 郑商所
    dictExchangeID['S'] =  EnumExchangeIDType.SHFE.name #上期所

    def __init__(self,eventEngine=None,common=None,account_ApiTypeDict=None,parent=None):
        super(Trading,self).__init__(eventEngine,common,parent)
        self.__eventEngine=eventEngine
        self.__common=common
        #self.__order=order_Data
        #self.Td_Api_List=td_api_list
        self.width = 100
        self.height = 25
        self.instrumentid =''
        self.investor_name_list=[]
        self.account_apiType=account_ApiTypeDict
        self.exchange_ApiType={} # 交易所对应的Api类型映射
        self.initUi()
        self.registerEvent()

    def registerEvent(self):
        self.signal_trading.connect(self.investorName)
        self.__eventEngine.register(EVENT_INVESTOR,self.signal_trading.emit)

    def investorName(self,event):
        #显示投资者名称
        #print u'交易者name==',event.dict_['data']
        #investor_N=event.dict_['data']['InvestorName'].decode('GBK')
        investor_ID=event.dict_['data']['InvestorID'].decode('GBK')
        investor_Filed=investor_ID # +'-'+investor_N
        if investor_Filed not in self.investor_name_list:
            self.investor_name_list.append(investor_Filed)   # 把账户名称和账户ID合在一起显示
        dic_investor_ID={}
        for n in range(len(self.investor_name_list)):
            target=self.investor_name_list[n]
            dic_investor_ID[n]=target
        #print u'useid==',dic_investor_ID
        self.cb_Name.clear()
        self.cb_Name.addItems(dic_investor_ID.values())

    def setLabels(self,text):
        """给label控件赋属性值"""
        labels=QtGui.QLabel(text)
        labels.setFixedHeight(self.height)
        labels.setFixedWidth(self.width)
        labels.setBackgroundRole(QtGui.QPalette.Highlight)
        return labels

    def initUi(self):
        #交易界面
        self.setWindowTitle(u'交易')
        ID=u'合约代码'
        labelID=self.setLabels(ID)
        account=u'交易账户'
        labelName=self.setLabels(account)
        exchangeid=u'交易所'
        labelExchangeid=self.setLabels(exchangeid)
        direction =u'买卖' #买卖申购赎回
        labelDirection=self.setLabels(direction)
        offset =u'开平'
        labelOffset=self.setLabels(offset)
        price = u'价格'
        labelPrice=self.setLabels(price)
        volume = u'数量'
        labelVolume=self.setLabels(volume)
        #labelPriceType = QtGui.QLabel(u'价格类型')
        #investor_name=self.investor_name.encode('GBK')  #获取账户名称
        #print 'investor_name==',investor_name

        self.lineID = QtGui.QLineEdit()
        self.lineID.setFixedHeight(self.height)

        self.cb_Name = QtGui.QComboBox()
        self.cb_Name.setFixedHeight(self.height)
            #self.lineName.setText(u'股票量化宽客积极1号')

        self.comboDirection = QtGui.QComboBox()
        self.comboDirection.addItems(self.dictDirection.values())
        self.comboDirection.setFixedHeight(self.height)

        self.comboOffset = QtGui.QComboBox()
        self.comboOffset.addItems(self.dictOffset.values())
        self.comboOffset.setFixedHeight(self.height)

        self.combExchangeid=QtGui.QComboBox()
        self.combExchangeid.addItems(self.dictExchangeID.values())
        self.combExchangeid.setFixedHeight(self.height)

        self.spinPrice=QtGui.QDoubleSpinBox()
        self.spinPrice.setMinimum(0.00)
        self.spinPrice.setMaximum(100000)
        self.spinPrice.setDecimals(2)
        #self.spinPrice.setValue(3825)

        self.spinVol=QtGui.QSpinBox()
        self.spinVol.setMinimum(1)
        self.spinVol.setMaximum(1000000)

        grid=QtGui.QGridLayout()
        grid.addWidget(labelID,0,0)
        grid.addWidget(labelName,1,0)
        grid.addWidget(labelExchangeid, 2, 0)
        grid.addWidget(labelDirection,3,0)
        grid.addWidget(labelOffset,4,0)
        grid.addWidget(labelPrice,5,0)
        grid.addWidget(labelVolume,6,0)
        grid.addWidget(self.lineID,0,1)
        grid.addWidget(self.cb_Name,1,1)
        grid.addWidget(self.combExchangeid,2,1)
        grid.addWidget(self.comboDirection,3,1)
        grid.addWidget(self.comboOffset,4,1)
        grid.addWidget(self.spinPrice,5,1)
        grid.addWidget(self.spinVol,6,1)

        orderinsert_btn = QtGui.QPushButton(u'下 单')  # 下单按钮
        orderinsert_btn.setFixedHeight(38)
        orderinsert_btn.setBackgroundRole(QtGui.QPalette.HighlightedText)
        #orderinsert_btn.setFont(QtGui.QFont(u'song',13))
        orderinsert_btn.setFlat(False)  #如果是True按钮会隐形
        orderinsert_btn.setToolTip(u'入市有风险！')
        orderinsert_btn.setStyleSheet('''color:blue;border-width:100;font:bold 18px''')


        qhBox=QtGui.QHBoxLayout()
        qhBox.addLayout(grid)

        qvBox=QtGui.QVBoxLayout()
        qvBox.addLayout(qhBox)
        qvBox.addWidget(orderinsert_btn)
        self.setLayout(qvBox)
        orderinsert_btn.clicked.connect(self.order_insert)   #点击下单

    def order_insert(self):
        #下单
        code=str(self.lineID.text())
        account=str(self.cb_Name.currentText())
        ex_id=unicode(self.combExchangeid.currentText())
        offerset = unicode(self.comboOffset.currentText())
        direction_text = unicode(self.comboDirection.currentText())
        price = float(self.spinPrice.text())
        vol = int(self.spinVol.text())
        if code and ex_id and offerset and direction_text and price>0 and vol>0:
            api_type = self.account_apiType[account]  # 调出该账号对应的API类型
            print u'收到委托指令', code, ex_id, offerset, direction_text, price, vol,api_type
            #def sendOrder(self, instrumentid, exchangeid, price, volume, direction, offset,api_type=None):
            self.__common.sendOrder(code,ex_id,price,vol,direction_text,offerset,api_type)
        else:
            event = Event(type_=EVENT_LOG)
            event.dict_['log']=u'委托失败，请检查委托的各要素是否填写正确'
            self.__eventEngine.put(event)

    def contextMenuEvent(self, event):
        #交易控件点击右键pass掉
        pass

class MarketData(BaseWidget):

    def __init__(self,eventEngine=None,common=None,colWidth=0,parent=None):
        super(MarketData,self).__init__(eventEngine,common,parent)
        self.__engine=eventEngine
        self.title=u'市场行情'
        self.columnsDict=OrderedDict()
        self.columnsDict['Name'] = u'指数名称'
        self.columnsDict['Code'] = u'指数代码'
        self.columnsDict['LastPrice'] = u'最新价'
        self.columnsDict['ZhangDie_Rate'] = u'涨跌幅'
        self.columnsDict['ZhangDie_num'] = u'涨跌额'
        self.columnsDict['HightestPrice'] = u'最高价'
        self.columnsDict['LowestPrice'] = u'最低阶'
        self.columnsDict['OpenPrice'] = u'开盘价'
        self.columnsDict['Amplitude_Rate'] = u'振幅'
        self.columnsDict['PreCloesPrice'] = u'昨收价'
        self.columnsDict['Up_Time'] = u'行情时间'
        self.initUi(self.title,self.columnsDict,self.font)
        self.EVENT_Type = EVENT_INDEX_MARKETDATA
        self.registerEvent(self.EVENT_Type)
        self.dictData={}
        self.dictLabels={}
        eachWidth=colWidth/len(self.columnsDict)
        for col, label in enumerate(self.columnsDict.keys()):
            self.setColumnWidth(col, eachWidth)  # 把第一列的宽度修改为N  QTableWidget
        #self.setColumnWidth(8,90) # 第九列宽度修改为N

    def rightKeyCsvDatas(self):
        pass

    def updateDatas(self,event):
        """更新行情"""
        data = event.dict_['data']
        instrumentid = data['Code']
        # 如果之前已经收到过这个账户的数据, 则直接更新
        if instrumentid in self.dictData and len(self.dictData)>0:
            #print 'instrumentid==',instrumentid
            #print 'self.dictData.count==',len(self.dictData)
            d = self.dictData[instrumentid]
            #print 'd==',d
            for label, cell in d.items():
                if label != 'Name':
                    value = str(data[label])
                else:
                    value = data['Name']
                cell.setText(value)
        # 否则插入新的一行，并更新
        else:
            row = self.rowCount()
            self.insertRow(row)
            d = {}
            #print 'self.columnsDict==',self.columnsDict
            for col, label in enumerate(self.columnsDict.keys()):

                if label != 'Name':
                    # print 'clo,label==',col,label
                    value = str(data[label])
                    cell = QtGui.QTableWidgetItem(value)
                    cell.setBackgroundColor(QColor(0, 5, 10))
                    if label == 'Code':
                        cell.setTextColor(QColor(255, 255, 0))
                    elif label == 'Up_Time':
                        cell.setTextColor(QColor(255, 255, 255))  # 200, 30, 30))
                    elif label == 'ZhangDie_Rate':
                        if value > 0.0:
                            cell.setTextColor(QColor(255, 0, 0))  # 180, 90, 60))
                        else:
                            cell.setTextColor(QColor(100, 200, 100))
                    elif label == 'ZhangDie_num':
                        cell.setTextColor(QColor(255, 255, 255))  # 193,210,150
                    elif label == 'LastPrice':
                        if value > data['PreCloesPrice']:
                            cell.setTextColor(QColor(255, 0, 0))
                        else:
                            cell.setTextColor(QColor(100, 200, 100))
                    elif label == 'Amplitude_Rate':
                        cell.setTextColor(QColor(180, 90, 60))
                    elif label == 'Trade_Num':
                        cell.setTextColor(QColor(200, 200, 80))
                    elif label == 'PreCloesPrice':
                        cell.setTextColor(QColor(255, 255, 255))  # 100, 200, 100))
                    elif label == 'HightestPrice':
                        if value > data['PreCloesPrice']:
                            cell.setTextColor(QColor(255, 0, 0))
                        else:
                            cell.setTextColor(QColor(100, 200, 100))
                    elif label == 'LowestPrice':
                        if value > data['PreCloesPrice']:
                            cell.setTextColor(QColor(255, 0, 0))
                        else:
                            cell.setTextColor(QColor(100, 200, 100))
                    elif label == 'OpenPrice':
                        if value > data['PreCloesPrice']:
                            cell.setTextColor(QColor(255, 0, 0))
                        else:
                            cell.setTextColor(QColor(100, 200, 100))
                    else:
                        cell.setTextColor(QColor(100, 200, 100))

                    cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.setItem(row, col, cell)
                    d[label] = cell
                else:
                    name = data['Name']
                    cell = QtGui.QTableWidgetItem(name)
                    cell.setBackgroundColor(QColor(0, 5, 10))
                    cell.setTextColor(QColor(255, 200, 100))
                    cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.setItem(row, col, cell)
                    d[label] = cell
            self.dictData[instrumentid] = d

            # ----------------------------------------------------------------------

    def contextMenuEvent(self, event):
        #市场行情界面点击右键的时候就pass掉
        pass

class LoginAccount(QtGui.QDialog):
    """登陆行情和交易账号的界面"""
    def __init__(self,eventEngine, common, parent=None):
        #QtGui.QWidget.__init__(self, parent)
        super(LoginAccount,self).__init__(parent)
        self.setGeometry(600, 300, 800, 500)
        self.form_Main = QtGui.QDialog()
        self.__eventEngine = eventEngine  # 私有对象 【该模块是event->事件调度各种event】
        self.__common = common  # 初始化Common【该模块是暴露了Md和Td Api所有给用户可以调用的接口】
        self.font = QtGui.QFont(u'微软雅黑', 12)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)  # 模态窗口
        # self.lbl = QtGui.QLabel()
        # self.lbl.adjustSize()  # 根据窗体的内容动态的改变窗体大小
        self.setWindowTitle(u"登陆设置")  # 确定窗体的名称
        self.setWindowIcon(QIcon('Resource/Main_tubiao.png'))
        self.md_get = 0
        self.td_get = 0
        self.md_file_name = r'api_set\MD_API_Set.ini'
        self.td_file_name = r'api_set\TD_API_Set.ini'
        self.setFont(self.font)
        ############################################################
        self.btn_Md_api = QtGui.QPushButton(u'行情Api设置', self)
        self.btn_Md_api.resize(self.btn_Md_api.sizeHint())
        self.btn_Md_api.setGeometry(300, 230, 191, 31)

        # 行情Api button的clicked事件
        self.btn_Md_api.clicked.connect(self.on_click_md)
        self.btn_Td_api = QtGui.QPushButton(u'交易Api设置', self)
        self.btn_Td_api.resize(self.btn_Td_api.sizeHint())
        self.btn_Td_api.setGeometry(300, 180, 191, 31)
        # 交易Api button的clicked事件
        self.btn_Td_api.clicked.connect(self.on_click_td)
        self.btn_Login = QtGui.QPushButton(u'确    定', self)
        self.btn_Login.resize(self.btn_Login.sizeHint())
        self.btn_Login.setGeometry(300, 280, 191, 41)
        # 点击登录后就退出主窗体
        # self.btn_Login.clicked.connect(self.close)
        self.btn_Login.clicked.connect(self.close_MainUI)
        ############################################################

    # 调用Md的跳出窗体
    def on_click_md(self):
        self.md = Mdapi_UI_Window(self.__eventEngine)
        self.md.show()
        self.md_get += 1
        self.md.exec_()

    # 调用Td的跳出窗体
    def on_click_td(self):
        self.td = Tdapi_UI_Window(self.__eventEngine)
        self.td.show()
        self.td_get += 1
        self.td.exec_()

    def closeEvent(self, QCloseEvent):
        # 如果点击了主窗体右上角的×就会触发QWidget的closeEvent方法
        if self.md_get >= 1 or self.td_get >= 1:
            msg = QtGui.QMessageBox.question(self, u'警告', u"确认退出?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                             QtGui.QMessageBox.No)  # (消息框标题, 显示消息, 选项 | 选项, 默认选项)
            if msg == QMessageBox.Yes:
                if self.md_get >= 1:
                    self.md.close()
                if self.td_get >= 1:
                    self.td.close()

                QCloseEvent.accept()
            else:
                QCloseEvent.ignore()

    def close_MainUI(self):
        # 判断子窗体是否没有关闭，如果没关闭则全部关闭
        if self.td_get >= 1:
            self.td.close()
            self.td_get = 0
        if self.md_get >= 1:
            self.md.close()
            self.md_get = 0

        if os.path.exists(self.md_file_name):
            if os.path.getsize(self.md_file_name) > 2:
                event = Event(type_=EVENT_LOG)
                event.dict_['log'] = u'行情账号已配置好，即将登陆...'
                self.__eventEngine.put(event)
            else:
                QMessageBox.warning(self, u'警告', u'行情账号没设置好，请检查', QMessageBox.Yes, QMessageBox.No)
                return
        else:
            QMessageBox.warning(self, u'警告', u'行情账号没设置好，请检查', QMessageBox.Yes, QMessageBox.No)
            return

        if os.path.exists(self.td_file_name):
            if os.path.getsize(self.td_file_name) > 2:
                event = Event(type_=EVENT_LOG)
                event.dict_['log'] = u'交易账号已配置好，即将登陆...'
                self.__eventEngine.put(event)
            else:
                QMessageBox.warning(self, u'警告', u'交易账号没设置好，请检查', QMessageBox.Yes, QMessageBox.No)
                return
        else:
            QMessageBox.warning(self, u'警告', u'交易账号没设置好，请检查', QMessageBox.Yes, QMessageBox.No)
            return

        self.close()  # 退出主窗体界面
        time.sleep(0.2)
        #main_window = Main_UI_Window(self.__eventEngine, self.__common, self) #Center_Window
        #main_window.show()
        # main_window.showMaximized()

    def paintEvent(self, event):
        # 加背景图片
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), QPixmap('Resource/login.png'))

class ApiSetUi(QtGui.QDialog):
    def __init__(self,eventEngine=None,parent=None):
        super(ApiSetUi, self).__init__(parent)
        #self.setObjectName("Md_Api")
        self.engine=eventEngine
        self.file_name ='' #r'api_set\MD_API_Set.ini'
        self.sectionDict = {} # 存储读取到本地的所有账号信息
        self.table_count=0
        self.len_column=0
        self.title=''
        self.setWindowTitle(self.title)
        self.font = QtGui.QFont(u'微软雅黑', 12)
        self.setFont(self.font)
        self.api_list=''

    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.engine.put(event)

    def new_ApiUi(self):
        try:
            self.setGeometry(500, 300, 1000, 500)
            self.setWindowIcon(QIcon('Resource/Main_tubiao.png'))
            # 列头名称
            self.Api_list_name = [u'账户', u'登录密码', u'Api类型', u'服务器地址', u'BrokerID', u'通讯协议', u'扩展字段']
            cf = configparser.ConfigParser()
            cf.read(self.file_name)  # self.file_name 也可以是一个不存在的文件
            if os.path.exists(self.file_name):
                if os.path.getsize(self.file_name):
                    try:
                        for n in cf.sections():
                            #print 'section==', n
                            userID=cf.get(n,'userID')
                            pwd=cf.get(n,'pwd')
                            apiType=cf.get(n,'apiType')
                            IP=cf.get(n,'IP')
                            brokeID=cf.get(n,'brokeID')
                            protocol=cf.get(n,'protocol')
                            extended=cf.get(n,'extended')
                            sec_list=[userID,pwd,apiType,IP,brokeID,protocol,extended]
                            self.sectionDict[n]=sec_list
                        table_c = len(self.sectionDict.keys())
                    except:
                        table_c=2
                else:
                    table_c = 2
            else:
                table_c = 2

            self.table_count = table_c
            self.len_column=len(self.Api_list_name)
            self.mytable = QTableWidget(self.table_count,self.len_column)
            #self.mytable.setColumnCount(len(self.Api_list_name))
            self.mytable.setHorizontalHeaderLabels(self.Api_list_name)  # 设置列头名
            self.mytable.setAlternatingRowColors(True)  # 隔行改变颜色
            self.mytable.setStyleSheet('''color:orange''')
            self.mytable.setColumnWidth(2,150)
            self.mytable.setColumnWidth(5, 190)
            self.mytable.setColumnWidth(3, 155)
            layout = QHBoxLayout()
            layout.addWidget(self.mytable)
        except Exception,e:
            self.log(e)
        try:
            ################################本地有数据，读取并写入到界面显示#################################
            if os.path.exists(self.file_name):
                if os.path.getsize(self.file_name):
                    ks_=-1
                    #-----------------本地有数据，读取并写入到界面显示#-------------------------
                    for n,values in self.sectionDict.items():
                        newItem=self.sectionDict[n]
                        ks_+=1
                        for j in range(self.len_column):
                            k=newItem[j]
                            if k != k:  # nan != nan  用于判断是否是nan
                                continue
                            import locale
                            mycode = locale.getpreferredencoding()  ##获取到的是本地的编码  gbk
                            code=QTextCodec.codecForName('utf-8')    ##用utf-8作为QTextCodec的编码
                            QTextCodec.setCodecForLocale(code)
                            QTextCodec.setCodecForTr(code)
                            QTextCodec.setCodecForCStrings(code)

                            if j==2: # 第三列 API的类型，添加一个combox给用户可选择新的API的机会
                                self.mycombo_new = QComboBox()  # 生成一个QComboBox对象(下拉菜单-->辅助用户在多种可选择性选项中选择其中一项)
                                api_ListNew=list(self.api_list)
                                api_ListNew.remove(k)
                                api_ListNew.insert(0,k)
                                self.mycombo_new.addItems(api_ListNew)
                                self.mytable.setCellWidget(ks_,j,self.mycombo_new)
                            else:
                                item_=QTableWidgetItem("{}".format(k))
                                item_.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignLeft)
                                self.mytable.setItem(ks_,j,item_)
                    self.setFont(self.font)
                    # -----------------本地有数据，读取并写入到界面显示#-------------------------
                else:
                    ######################################如果本地没有数据就手动写入###########################################
                    #print 'csv文件为空,size==',file_size
                    for n in range(self.mytable.rowCount()):
                        self.mycombo = QComboBox()  # 生成一个QComboBox对象(下拉菜单-->辅助用户在多种可选择性选项中选择其中一项)
                        self.nameList = self.api_list
                        self.mycombo.addItems(self.nameList)
                        self.mytable.setCellWidget(n, 2, self.mycombo)  #
                    # self.mytable.verticalHeader().setVisible(False)  # 关闭左边的垂直表头
                okButton = QtGui.QPushButton(u'确 认')
                okButton.setStyleSheet('''color:yellow''')
                okButton.setFont(self.font)
                self.connect(okButton, QtCore.SIGNAL('clicked()'), self.save_Data)
                layout.addWidget(okButton)

                ######################################如果本地没有数据就手动写入###########################################
            else:
                msg=QMessageBox.warning(self,u'提示',u'行情API设置文件不存在,将自动创建文件?',QMessageBox.Yes,QMessageBox.No)
                if msg==QMessageBox.Yes:
                    for n in range(self.mytable.rowCount()):
                        self.mycombo = QComboBox()  # 生成一个QComboBox对象(下拉菜单-->辅助用户在多种可选择性选项中选择其中一项)
                        self.nameList =self.api_list
                        self.mycombo.addItems(self.nameList)
                        self.mytable.setCellWidget(n, 2, self.mycombo)  #
                    # self.mytable.verticalHeader().setVisible(False)  # 关闭左边的垂直表头
                    okButton = QtGui.QPushButton(u'确 认')
                    self.connect(okButton, QtCore.SIGNAL('clicked()'), self.save_Data)
                    layout.addWidget(okButton)
                else:
                    print u'警告：本地文件没创建'
                    QMessageBox.warning(self, u'警告', u'本地文件没创建,将影响账户的登录,请重新启动并创建文件！', QMessageBox.Yes, QMessageBox.No)
            self.setLayout(layout)
        except Exception,e:
            self.log(e)

    def save_Data(self):
        #保存QtableWiget上的数据(Md_api_set的数据)
        try:
            msg=QMessageBox.warning(self,u"提示",u'数据将保存到本地',QMessageBox.Yes,QMessageBox.No)
            if msg==QMessageBox.Yes:
                #self.file_name=r'md_api_set.csv'     #getSaveFileName()函数 -->‘另存为’ vs   #getOpenFileName()函数   “打开”
                cf = configparser.ConfigParser()
                cf.read(self.file_name)  # self.file_name 也可以是一个不存在的文件
                for n in range(self.mytable.rowCount()):   #行
                    data_save_list = []
                    d_item = self.mytable.item(n, 1)
                    if d_item == None:
                        continue
                    for m in range(len(self.Api_list_name)): #列  ####################此处Td/Md很可能不一样
                        table_cell_value=self.mytable.item(n,m)
                        if table_cell_value==None:
                            #cb_currenttext=self.mycombo.currentText()  ########u'此处有问题，如何找出当前索引的QCombobox的值'
                            #cb_itemtext=self.mycombo.itemText(n)
                            table_cell=self.mytable.cellWidget(n,m)
                            if table_cell==None:
                                table_cell_text=''
                            else:
                                table_cell_text=unicode(table_cell.currentText().toUtf8(),'utf-8','ignore').encode('utf-8')
                            data_save_list.append(table_cell_text)
                        else:
                            string_text=table_cell_value.text()
                            data2=unicode(string_text.toUtf8(), 'utf-8', 'ignore').encode('utf-8')
                            data_save_list.append(str(data2))
                    try:
                        sec = data_save_list[0]  # 账号中文名
                        if sec not in cf.sections():
                            cf.add_section(sec)  # 注意如果文件中已经存在相应的项目，则不能在增加同名的节
                            self.setIniFileData(cf,sec,data_save_list)
                        else:
                            self.setIniFileData(cf,sec,data_save_list)
                        cf.write(open(self.file_name, 'w'))
                    except configparser.DuplicateOptionError:
                        self.log("Section {} already exists".format(sec))
                log= u'api存储数据完毕'
                self.log(log)
            elif msg==QMessageBox.No:
                log= u'警告:数据没保存'
                self.log(log)
        except Exception,e:
            self.log(e)
        self.close() # 数据保存完后，自动关闭当前UI
    # 加背景图片
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), QPixmap("Resource/Api_Set.png"))

    def setIniFileData(self,cf,sec,data_save_list):
        """把数据写到本地ini文件"""
        cf.set(sec, u'userID', data_save_list[0])  # 使用cf.set()在节group3中增加新的参数
        cf.set(sec, u"pwd", data_save_list[1])
        cf.set(sec, u"apiType", data_save_list[2])
        cf.set(sec, u"IP", data_save_list[3])
        cf.set(sec, u"brokeID", data_save_list[4])
        cf.set(sec, u"protocol", data_save_list[5])  # 通讯协议
        cf.set(sec, u"extended", data_save_list[6])  # 扩展字段

class Mdapi_UI_Window(ApiSetUi):
    def __init__(self,eventEngine=None,parent=None):
        super(Mdapi_UI_Window,self).__init__(eventEngine,parent)
        self.engine=eventEngine
        self.title=u'行情Api设置'
        self.file_name=r'api_set\MD_API_Set.ini'
        self.api_list = (EnumQuoteApiType.CTP_Future_Md.name, EnumQuoteApiType.FeiMa_Md.name, EnumQuoteApiType.HongHui_Stock_Md.name,EnumQuoteApiType.HengSheng_T2_Stock_Md.name, EnumQuoteApiType.Fix_GuoXin_Stock_Md.name)
        self.new_ApiUi()

class Tdapi_UI_Window(ApiSetUi):
    def __init__(self,eventEngine=None,parent=None):
        super(Tdapi_UI_Window,self).__init__(eventEngine,parent)
        self.engine=eventEngine
        self.title=u'交易Api设置'
        self.file_name=r'api_set\TD_API_Set.ini'
        self.api_list=(EnumTradeApiType.CTP_Future_Td.name,EnumTradeApiType.GuoTaiJunAn_Stock_Td.name,EnumTradeApiType.HengSheng_T2_Stock_Td.name,EnumTradeApiType.Fix_GuoXin_Stock_Td.name)
        self.new_ApiUi()

class AboutSystem(QtGui.QDialog):
    """显示关于信息"""
    def __init__(self,parent=None):
        super(AboutSystem,self).__init__(parent)
        self.initUI()

    def initUI(self):
        """介绍本系统"""
        self.setWindowTitle(u'关于本系统')
        text=u"""
        本系统在参考VN系统、SGD公司的交易系统框架的基础上研发出来的，在这里非常感谢这些前辈，谢谢！
        ===============================================
        +   本系统支持股票和期货的程序化交易           + 
        +   股票---->期现套利(篮子下单),程序化选股     +
        +   期货---->程序化择时,跨期和跨品种套利       + 
        +   联系方式:1013359736                        +               
        ==============================================
        """
        lable=QtGui.QLabel()
        lable.setText(text)
        vbox=QtGui.QVBoxLayout()
        vbox.addWidget(lable)
        self.setLayout(vbox)


class Center_Window(QtGui.QMainWindow):
    signalInvestor = QtCore.pyqtSignal(type(Event()))  # 投资者名称
    signalLog = QtCore.pyqtSignal(type(Event()))  # log

    def __init__(self,eventEngine,common,parent=None):
        super(Center_Window,self).__init__(parent)
        print u'到了中暑引擎'
        self.colHight=1000  #colHight
        self.colWidth=1600
        self.setGeometry(200, 100, self.colWidth, self.colHight)
        #self.setWindowTitle(u"Trade 终端")  # 确定窗体的名称
        self.setWindowIcon(QIcon('Resource/Main_tubiao.png'))
        self.tdPath='api_set/TD_API_Set.ini'
        self.mdPath = 'api_set/MD_API_Set.ini'
        self.__eventEngine=eventEngine
        self.__common=common
        self.setWindowTitle(u'NewIsland')
        #self.setFixedSize(1800,1000)
        self.font = QtGui.QFont(u'微软雅黑', 12)
        self.logWidth = 600  # log（日志）这个ui的宽度
        self.tradingWidth=280 # trading(交易)这个ui的宽度
        self.account_PositionWidth=self.colWidth - self.logWidth
        self.account_ApiTypeDict={} # 账号对应的API
        self.registerEvent()
        # 固定订阅腾讯接口的指数合约
        self.__common.md_Login('100888', '123465', 'tcp:\\192.168.1.2.3:45678', '10133', api_type=EnumQuoteApiType.EM_DongFang_Finance_Md.name)
        self.setFont(self.font)
        self.loginTd_Md_Account(self.tdPath,self.mdPath)
        self.initUi()


    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.__eventEngine.put(event)

    def login_Sections(self,path=None,tm=None):
        sectionDict = {}
        try:
            if os.path.exists(path):
                if os.path.getsize(path):
                    cf_login = configparser.ConfigParser()
                    cf_login.read(path)
                    for n in cf_login.sections():
                        userID = cf_login.get(n, 'userID')
                        pwd = cf_login.get(n, 'pwd')
                        apiType = cf_login.get(n, 'apiType')
                        IP = cf_login.get(n, 'IP')
                        brokeID = cf_login.get(n, 'brokeID')
                        protocol = cf_login.get(n, 'protocol') # 通讯协议
                        extended = cf_login.get(n, 'extended') # 扩展字段
                        if tm=='td': # 只记录交易账号的API
                            self.account_ApiTypeDict[userID]=apiType
                        sec_list = [userID, pwd, apiType, IP, brokeID, protocol, extended]
                        sectionDict[n] = sec_list
                else:
                    self.log(u'账号文件是空的，请填写完成后再登陆')
            else:
                self.log(u'账号文件不存在，请重新设置')
        except Exception,e:
            self.log(e)
        return sectionDict

    def loginTd_Md_Account(self,tdPath,mdPath):
        """登陆行情和交易账号"""
        quoteField=self.login_Sections(mdPath,'md')
        self.loginMethod(quoteField,self.__common.md_Login)

        tradeField=self.login_Sections(tdPath,'td')
        self.loginMethod(tradeField,self.__common.td_Login)

    def loginMethod(self,td_mdField,loginMethods):
        try:
            if td_mdField:
                fields_Data=(td_mdField.values())
                for fields in fields_Data:
                    userID=fields[0]
                    pwd=fields[1]
                    apiType=fields[2]
                    ip=fields[3]
                    brokeID=fields[4]
                    protocol=fields[5] # 通讯协议
                    extended=fields[6] # 扩展字段
                    # def md_Login(self,address,userid, password, brokerid,api_Type=None)
                    loginMethods(ip,userID,pwd,brokeID,apiType)
        except Exception,e:
            self.log(e)

    def initUi(self):
        """初始化主窗口"""

        self.log_data = Log_Data(self.__eventEngine, self.__common,self.logWidth)  # LogMonitor
        self.account = AccountData(self.__eventEngine, self.__common,self.account_PositionWidth,self)
        self.position = PositionData(self.__eventEngine, self.__common,self.account_PositionWidth,self)
        self.trade = Trade_Data(self.__eventEngine, self.__common,self.colWidth,self)
        self.order = Order_Data(self.__eventEngine, self.__common, self.account_ApiTypeDict,self.colWidth,self)
        self.marketdata = MarketData(self.__eventEngine, self.__common, self.colWidth-self.tradingWidth,self)
        self.trading = Trading(self.__eventEngine, self.__common, self.account_ApiTypeDict,self)
        self.system = AboutSystem(self)

        righttab = QtGui.QTabWidget()
        righttab.addTab(self.position, u'持仓')
        righttab.addTab(self.account, u'账户')
        righttab.setFont(self.font)
        righttab.setFixedWidth(self.account_PositionWidth)
        # righttab.addTab(self.log_data,u'日志')

        lefttab = QtGui.QTabWidget()
        lefttab.addTab(self.order, u'委托')
        lefttab.addTab(self.trade, u'成交')
        lefttab.setFont(self.font)

        log_tab = QtGui.QTabWidget()
        log_tab.addTab(self.log_data, u'日志')
        log_tab.setFixedWidth(self.logWidth)
        log_tab.setFont(self.font)

        market_tab=QtGui.QTabWidget()
        market_tab.addTab(self.marketdata,u'市场行情')
        market_tab.setFont(self.font)

        self.trading.setMaximumWidth(self.tradingWidth)
        self.trading.setFixedHeight(300)
        tradingVBox = QtGui.QVBoxLayout()
        tradingVBox.addWidget(self.trading)
        tradingVBox.addStretch()

        upHBox = QtGui.QHBoxLayout()  # 水平布局->在水平方向上排列控件 即：左右排列。
        upHBox.addLayout(tradingVBox)  # 将tradingVBox加入水平布局器
        upHBox.addWidget(market_tab)

        a_p_lHBox = QtGui.QHBoxLayout()  # account position log
        a_p_lHBox.addWidget(lefttab)

        t_oHBox = QtGui.QHBoxLayout()
        t_oHBox.addWidget(righttab)
        t_oHBox.addWidget(log_tab)

        marketHbox=QtGui.QHBoxLayout()
        marketHbox.addWidget(market_tab)

        vBox = QtGui.QVBoxLayout()  # 垂直布局->在垂直方向上排列控件 即：上下排列。
        vBox.addLayout(upHBox)  # 将trade_order_HBox加入垂直布局器
        vBox.addLayout(a_p_lHBox)
        vBox.addLayout(t_oHBox)
        #vBox.addLayout(marketHbox)
        # self.statusBar()
        # self.addToobar()
        centralwidget = QtGui.QWidget()
        centralwidget.setLayout(vBox)
        self.setCentralWidget(centralwidget)

        accountLogin=QtGui.QAction(u'登陆账号',self)
        accountLogin.setShortcut('Ctrl+L')
        accountLogin.triggered.connect(self.ui_Login)
        accountLogin.setFont(self.font)

        system = QtGui.QAction(u'关于系统', self)
        system.setShortcut('Ctrl+F')
        system.triggered.connect(self.aboutsystem)
        system.setFont(self.font)

        cancelall = QtGui.QAction(u'委托全撤', self)
        cancelall.setShortcut('Ctrl+F1')
        cancelall.triggered.connect(self.order.cancelAll)
        cancelall.setFont(self.font)

        strategy = QtGui.QAction(u'启动策略', self)
        strategy.setShortcut('Ctrl+N')
        strategy.setFont(self.font)
        strategy.triggered.connect(self.startStrategys)

        menu = self.menuBar()
        menu.setFont(self.font)
        sysmenu = menu.addMenu(u'系统')
        sysmenu.addAction(system)
        sysmenu.setFont(self.font)

        trade__menu = menu.addMenu(u'交易')
        trade__menu.addAction(cancelall)
        trade__menu.addAction(strategy)
        trade__menu.setFont(self.font)

        accountLoginMenu=menu.addMenu(u'账号')
        accountLoginMenu.addAction(accountLogin)
        accountLoginMenu.setFont(self.font)

    def startStrategys(self):
        from Resource.Strategys_UiEngine import StrategyUi
        self.strategyui=StrategyUi(self.__eventEngine,self.__common,self.account_ApiTypeDict)
        self.strategyui.show()

    def registerEvent(self):
        """监控"""
        self.signalInvestor.connect(self.investorName)
        #self.signalLog.connect(self.updateLog)
        self.__eventEngine.register(EVENT_INVESTOR, self.signalInvestor.emit)
        #self.__eventEngine.register(EVENT_LOG, self.signalLog.emit)

    def investorName(self,event):
        """显示投资者名称"""
        print u'到这里-->显示投资者名称-->'
        invertor=event.dict_['data']  #event.dict_['data']['InvestorName'].decode('GBK')
        self.setWindowTitle(invertor['InvestorName'].decode('GBK')+u' Win Trade 终端 - 永恒电信')

    def ui_Login(self):
        """登陆行情和交易账号的设置界面"""
        self.logintAcc=LoginAccount(self.__eventEngine,self.__common,self)
        self.logintAcc.show()

    def aboutsystem(self):
        # 打开介绍系统的界面
        self.system=AboutSystem(self)
        self.system.show()

    def orderCancelAll(self):
        """委托全撤"""
        self.order.cancelAll()

    def closeEvent(self, QCloseEvent):
        # 退出界面确认
        msg = QMessageBox.question(self, u'退出', u'确认退出?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No)
        if msg == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            print u'界面没关掉'
            QCloseEvent.ignore()

    def paintEvent(self, event):
        palettel=QtGui.QPalette()
        palettel.setBrush(self.backgroundRole(),QtGui.QBrush(QtGui.QPixmap('Resource/CenterWindow.png')))
        self.setPalette(palettel)