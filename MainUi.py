# coding:utf-8
"""
author=fenglelanya
learn more
"""

import ctypes,sys,qdarkstyle
from Resource.Common import *
from Resource.CentralEngine import *
from NewIsland_Center_Ui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtCore,QtGui,Qt


def mainUi():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vn.py demo')  # win7以下请注释掉该行
    app=QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('Resource/Main_tubiao.png'))
    app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
    com=Common()
    engine_=com.engine
    window=Center_Window(engine_,com)
    window.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    mainUi()
