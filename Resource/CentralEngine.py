# encoding: UTF-8
"""
author=fenglelanya
learn more

"""

# 系统模块
from Queue import Queue, Empty
from threading import Thread
from time import sleep
from collections import defaultdict

# 第三方模块
from PyQt4.QtCore import QTimer

# 自己开发的模块
from eventType import *


########################################################################
class EventEngine(object):

    # ----------------------------------------------------------------------
    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False

        # 事件处理线程
        self.__thread = Thread(target=self.__run)

        # 计时器，用于触发计时器事件
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__onTimer)

        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.__handlers = defaultdict(list)

    # ----------------------------------------------------------------------
    def __run(self):
        """引擎运行"""
        while self.__active == True:
            try:
                event = self.__queue.get(block=True, timeout=1)  # 获取事件的阻塞时间设为1秒
                self.__process(event)
            except Empty:
                pass

    # ----------------------------------------------------------------------
    def __process(self, event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.__handlers[event.type_]]

    # ----------------------------------------------------------------------
    def __onTimer(self):
        """向事件队列中存入计时器事件"""
        # 创建计时器事件
        event_ = Event(type_=EVENT_TIMER)
        # 向队列中存入计时器事件
        self.put(event_)

        # ----------------------------------------------------------------------

    def start(self):
        """引擎启动"""
        # 将引擎设为启动
        self.__active = True

        # 启动事件处理线程
        self.__thread.start()

        # 启动计时器，计时器事件间隔默认设定为1秒
        self.__timer.start(1000)

    # ----------------------------------------------------------------------
    def stop(self):
        """停止引擎"""
        # 将引擎设为停止
        self.__active = False

        # 停止计时器
        self.__timer.stop()

        # 等待事件处理线程退出
        self.__thread.join()

    # ----------------------------------------------------------------------
    def register(self, type_, handler):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无defaultDict会自动创建新的list
        handlerList = self.__handlers[type_]

        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)

    # ----------------------------------------------------------------------
    def unregister(self, type_, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        handlerList = self.__handlers[type_]

        # 如果该函数存在于列表中，则移除
        if handler in handlerList:
            handlerList.remove(handler)

        # 如果函数列表为空，则从引擎中移除该事件类型
        if not handlerList:
            del self.__handlers[type_]

    # ----------------------------------------------------------------------
    def put(self, event):
        """向事件队列中存入事件"""
        self.__queue.put(event)



class Event:
    """事件对象"""

    #----------------------------------------------------------------------
    def __init__(self, type_=None):
        self.type_ = type_      # 事件类型
        self.dict_ = {}         # 字典用于保存具体的事件数据
