# coding:utf-8
"""
author=fenglelanya
learn more
"""
import sys,os
sys.path.append('..')
from CentralEngine import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtCore,QtGui
from collections import OrderedDict
from strategy.BaseStrategy import Strategys

class GetStrategyFieldDatas(QtGui.QTableWidget):

    def __init__(self,eventEngine=None,strategyList=None,strategyField=None,strategys_Param=None,uiWidth=0,parent=None):
        super(GetStrategyFieldDatas,self).__init__(parent)
        self.strategys=strategyList  # 策略
        self.strategysfield=strategyField  # 策略的字段
        self.strategysparam=strategys_Param  # 策略的参数
        self.uiWidth=uiWidth
        self.engine=eventEngine
        self.setGeometry(300, 300, 600, 300)
        columnDict =OrderedDict()
        columnDict['strategyName']=u'策略名称'
        columnDict['author']=u'策略作者'
        columnDict['update']=u'更新时间'
        title=u'策略名称'
        self.initUi(title,columnDict,self.strategysfield)

    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.engine.put(event)

    def initUi(self,title,col,field):
        """"""
        self.setWindowTitle(title)
        rowCount = len(self.strategys)
        colCount = len(col)
        self.mytable = QTableWidget(rowCount, colCount)
        self.mytable.setHorizontalHeaderLabels(col.values())  # 设定列名
        for n in range(colCount):
            self.mytable.setColumnWidth(n, self.uiWidth / colCount)
        #self.setRowCount(len(self.strategys))
        #self.setColumnCount(len(col))  # self.setColumnCount(2)
        self.mytable.setAlternatingRowColors(True)  # 隔行改变颜色
        self.mytable.verticalHeader().setVisible(False)  # # 关闭左边的垂直表头
        self.mytable.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)  # 设为不可编辑状态
        self.mytable.setFont(QtGui.QFont(u'微软雅黑', 12))
        self.mytable.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择
        row_ = -1

        for k,v in field.items():
            row_+=1
            for c, label in enumerate(col.keys()):
                values=v[label]
                try:
                    cell=QtGui.QTableWidgetItem(values)
                    cell.setBackgroundColor(QColor(0, 5, 100))
                    cell.setTextColor(QColor(100, 200, 100))
                    cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignLeft)
                    self.mytable.setItem(row_,c,cell)
                except Exception,e:
                    self.log(e)


class GetStrategyParamDatas(QtGui.QDialog):
    """加载策略的时候给选定策略的参数赋值"""
    def __init__(self,eventEngine=None,paramDict=None,curStrategy=None,allStrategys=None,parent=None):
        super(GetStrategyParamDatas,self).__init__(parent)
        self.engine=eventEngine
        self.strategyParamDict = paramDict
        self.curStrategy_=curStrategy
        self.allStrategyDict=allStrategys
        self.colCount = 2
        self.colWidth=330
        self.colHight=400
        self.setGeometry(260, 300, self.colWidth, self.colHight)
        self.colDict=OrderedDict()
        self.colDict['1']=u'参数名称'
        self.colDict['2']=u'参数值'
        self.iniParamUi()

    def iniParamUi(self):
        self.setWindowTitle(u'策略参数')
        curParams_=self.strategyParamDict[self.curStrategy_]
        row_count=len(curParams_)
        col_count=2
        row_fields=curParams_.keys()
        self.mytable=QtGui.QTableWidget(row_count,col_count)
        self.mytable.setFont(QtGui.QFont(u'微软雅黑', 12))
        self.mytable.setHorizontalHeaderLabels(self.colDict.values())
        self.mytable.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter) # 列头文字居左（默认是居中）
        #self.mytable.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)  # 设为不可编辑状态
        for n in range(len(row_fields)):
            key=QTableWidgetItem(row_fields[n])
            #key.setBackgroundColor(QColor(60, 60, 12))
            key.setTextColor(QColor(180, 90, 60)) #QColor(100, 200, 100)
            key.setFlags(Qt.NoItemFlags)
            self.mytable.setItem(n,0,key)
            value_by_key=row_fields[n]
            cur_value=curParams_[value_by_key]
            value=QTableWidgetItem(str(cur_value))
            value.setTextColor(QColor(120, 160, 230))
            self.mytable.setItem(n,1,value)
        self.mytable.setAlternatingRowColors(True)  # 隔行改变颜色
        self.mytable.verticalHeader().setVisible(False)  # # 关闭左边的垂直表头
        len_col=len(self.colDict)
        for n in range(len_col):
            self.mytable.setColumnWidth(n,self.colWidth/len_col)
        OKBtn=QtGui.QPushButton(u'确  定')
        OKBtn.setStyleSheet('''color:yellow''')
        OKBtn.clicked.connect(self.closeCurUi)
        hbox = QHBoxLayout()
        hbox.addWidget(self.mytable)
        hbox.addWidget(OKBtn)

        self.setLayout(hbox)

    def closeCurUi(self):
        """关闭当前UI，同时更新策略的参数"""
        #msg=QtGui.QMessageBox.question(self,u'提示',u'将保存参数',QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        oringalParams=self.allStrategyDict[self.curStrategy_].parameter
        newParams ={}
        for r in range(self.mytable.rowCount()):
            paramName = unicode(self.mytable.item(r,0).text(),'gbk','ignore')
            paramValue= unicode(self.mytable.item(r,1).text(),'gbk','ignore')
            newParams[paramName]=paramValue

        for n in oringalParams.keys():
            if n in newParams:
                if oringalParams[n]!=newParams[n]: # 如果参数的值修改了
                    self.allStrategyDict[self.curStrategy_].parameter[n]=newParams[n]
                else:
                    continue
        self.close()

class StrategyUi(QtGui.QMainWindow):
    signal = QtCore.pyqtSignal(type(Event()))
    def __init__(self,eventEngine=None,common=None,account_ApiTypeDict=None,parent=None):
        super(StrategyUi,self).__init__(parent)
        self.UiWidth=700
        self.UiHight=400
        self.__eventEngine=eventEngine
        self.__common=common
        self.account_ApiDict=account_ApiTypeDict
        self.setGeometry(600, 300, self.UiWidth,self.UiHight)
        self.selectedStrategyDict=OrderedDict() # 当前选定的策略
        self.selectedStrategyFieldDict=OrderedDict() # 当前选定策略的三个字段
        self.selectedStrategyParamDict=OrderedDict() # 当前选定策略的所有参数
        self.loadedStrategyDict={}  # 已经加载过的策略
        self.startedStrategyDict={} # 已经启动过的策略
        self.endedStrategyDict={}   # 已经结束了的策略
        self.setWindowTitle(u"NewIsland Strategys Ui")  # 确定窗体的名称
        self.setWindowIcon(QIcon('Resource/Main_tubiao.png'))
        self.path=r'strategy/'
        self.font = QtGui.QFont(u'微软雅黑', 12)
        self.paramUiBool=False # False指的是没打开 True指的是打开了
        self.setFocus()  #不获得焦点
        self.initUi()

    def log(self,log):
        """打log"""
        event=Event(type_=EVENT_LOG)
        event.dict_['log']=log
        self.__eventEngine.put(event)

    def initUi(self):
        try:
            loadStrategy = QtGui.QPushButton(u'加载策略')
            loadStrategy.clicked.connect(self.loadStrategyValue)  #  self.btn_Md_api.clicked.connect(self.on_click_md)
            loadStrategy.setFont(self.font)
            loadStrategy.setStyleSheet('''color:brown''') #orderinsert_btn.setStyleSheet('''color:blue;border-width:100;font:bold 15px''')
            startStrategy = QtGui.QPushButton(u'启动策略')
            startStrategy.clicked.connect(self.starStrategyValue) #golden yellow
            startStrategy.setFont(self.font)
            startStrategy.setStyleSheet('''color:yellow''')
            stopStrategy = QtGui.QPushButton(u'退出策略')
            stopStrategy.clicked.connect(self.endStrategyVlue)  # golden yellow
            stopStrategy.setFont(self.font)
            stopStrategy.setStyleSheet('''color:green''')

            strategyFields=self.getStrategysName(self.path)
            self.strategyFieldData = GetStrategyFieldDatas(self.__eventEngine,strategyFields[0],strategyFields[1],strategyFields[2],self.UiWidth)
            self.strategy_Ui = QtGui.QTabWidget()
            self.strategy_Ui.addTab(self.strategyFieldData.mytable, u'策略名称')
            self.strategy_Ui.setFont(self.font)
            self.setFont(self.font)

            #self.strategyParamData=GetStrategyParamDatas(self.__eventEngine,strategyFields[2])
            #self.strategyParam_Ui=QtGui.QTabWidget()
            #self.strategyParam_Ui.addTab(self.strategyParamData,u'策略参数')
            #self.strategyParam_Ui.setFont(self.font)

            # 设置布局
            hbox2 = QtGui.QHBoxLayout()
            hbox2.addWidget(loadStrategy)
            hbox2.addWidget(startStrategy)
            hbox2.addWidget(stopStrategy)

            qvbox=QtGui.QVBoxLayout()
            qvbox.addLayout(hbox2)
            qvbox.addWidget(self.strategy_Ui)
            #qvbox.addWidget(self.strategyParam_Ui)

            qw=QtGui.QWidget()
            qw.setLayout(qvbox)

            self.setCentralWidget(qw)
        except Exception,e:
            self.log(u'StrategyUi-->iniUi 出现错误，请检查!')

    def getStrategysName(self,path):
        """根据指定目录获取所有策略名字"""
        strategys__=[]
        try:
            list_py=['BaseStrategy.py','BaseStrategy.pyc', '__init__.py', '__init__.pyc','EnumType.py','EnumType.pyc']
            data_list=os.listdir(path)
            resultStrategy=[n for n in data_list if n not in list_py]
            strategysData=[os.path.splitext(n)[0] for n in resultStrategy]
            strategys__=list(set(strategysData))
            strategys_Instance,strategys_Field,strategys_Param=self.getAllStrategyField(strategys__)
            return strategys__,strategys_Field,strategys_Param
        except Exception,e:
            self.log(e)
            return strategys__

    def getAllStrategyField(self,strategys__):
        """获取所有指定目录的py的字段"""
        for n in strategys__:
            m_path='strategy.'+n
            __import__(m_path)
            m=sys.modules[m_path]
            attstr=dir(m)
            for str in attstr:
                at = getattr(m, str)
                if type(at) == type and issubclass(at,Strategys) and at!=Strategys:
                    self.selectedStrategyDict[str]=at
                    fieldDict = {"author":at.author, "strategyName":at.strategyName, "update":at.update}
                    self.selectedStrategyFieldDict[str] = fieldDict
                    self.selectedStrategyParamDict[str] = at.parameter

        return self.selectedStrategyDict,self.selectedStrategyFieldDict,self.selectedStrategyParamDict

    def loadStrategyValue(self):
        """加载策略"""
        curStrategy=self.handleStrategy(self.loadedStrategyDict,u'加载')
        if len(self.selectedStrategyParamDict)>0 and curStrategy!=''and curStrategy!=None:
            """把策略的参数传递给Param界面"""
            #print u'加载策略-->当前选定的策略==',curStrategy
            params = self.selectedStrategyParamDict[curStrategy]
            self.curStrategyParams_=GetStrategyParamDatas(self.__eventEngine,self.selectedStrategyParamDict,curStrategy,self.selectedStrategyDict)
            self.curStrategyParams_.show()
            self.paramUiBool = True

    def starStrategyValue(self):
        """启动策略"""
        self.startEndStrategy(self.startedStrategyDict,u'启动')

    def endStrategyVlue(self):
        """停止策略"""
        self.startEndStrategy(self.endedStrategyDict,u'停止')

    def startEndStrategy(self,strategyDict,text_):
        '''用于启动或停止策略的封装'''
        try:
            dt=self.handleStrategy(strategyDict,text_)
            if len(strategyDict)>0 and dt!=''and dt!=None: # 说明已经有可以启动的策略
                strategy = strategyDict[dt]
                handel_Strategy=strategy(self.__eventEngine,self.__common,self.account_ApiDict)
                if text_==u'启动':
                    handel_Strategy.startStrategy()
                    self.log(u'启动了{}策略'.format(dt))
                elif text_==u'停止':
                    handel_Strategy.endStrategy()
                    self.log((u'停止了{}策略').format(dt))
        except Exception,e:
            self.log(u'%s策略出现问题，请检查-->(%s)！'%(text_,e))

    def handleStrategy(self,dict,text_):
        """操作策略(加载、启动、停止)"""
        try:
            curStr=self.strategyFieldData.mytable.selectedItems()
            if len(curStr)>0:
                currentStrategy = curStr[0] # list的第一个元素就是策略的名称
                curStrategy=currentStrategy.text()
                dt = unicode(curStrategy, 'gbk', 'ignore')
                for k,v in self.selectedStrategyDict.items():
                    if dt not in self.selectedStrategyDict:
                        self.log(u'策略%s不存在，不能%s该策略'%(dt,text_))
                        return
                    else:
                        if dt ==k:
                            if dt not in dict:
                                dict[dt]=v
                                return dt
                            else:
                                self.log(u'策略%s已%s,请不要重复操作策略'%(dt,text_))
                                return ''


            else:
                self.log(u'没选定策略，请选择您要{}的策略！'.format(text_))
        except Exception,e:
            self.log(e)
            return ''

    def closeEvent(self,QCloseEvent):
        """关闭界面"""
        msg=QtGui.QMessageBox.question(self, u'警告', u"确认退出?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                             QtGui.QMessageBox.No)  # (消息框标题, 显示消息, 选项 | 选项, 默认选项)
        if msg==QMessageBox.Yes:
            if self.paramUiBool:
                self.curStrategyParams_.close()
            QCloseEvent.accept()
        elif msg==QMessageBox.No:
            QCloseEvent.ignore()