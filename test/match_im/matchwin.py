# /usr/bin/dev python
# -*- coding: utf-8 -*-

import os
import sys
import time
from PIL import Image, ImageGrab
import win32gui
import win32con
import pyautogui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from match_widget import Ui_match_win


class AutoLocate(QThread):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, filepath='', win_name='阴阳师-网易游戏'):
        super(AutoLocate, self).__init__(parent)
        self.win_name = win_name
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.stop = False

    def display_msg(self, msg):
        '''输出日志到框内'''
        self.sendmsg.emit(msg, 'Info')
        print(msg)

    def stop_run(self):
        self.stop = True

    def run(self):
        win_name = self.win_name
        yys_handler = win32gui.FindWindow(0, win_name)  # 获取窗口句柄
        if yys_handler == 0:
            self.display_msg('获取不到阴阳师窗体' + str(yys_handler))
            return
        else:
            self.display_msg('获取到阴阳师窗体' + str(yys_handler))

        x_top, y_top, x_bottom, y_bottom = win32gui.GetWindowRect(yys_handler)
        win_width = x_bottom - x_top
        win_height = y_bottom - y_top
        self.display_msg('位置信息：({0},{1}), ({2},{3})'.format(
            x_top, y_top, x_bottom, y_bottom))

        win_width = 1152
        win_height = 679
        x_bottom = x_top + win_width
        y_bottom = y_top + win_height
        try:
            win32gui.SetWindowPos(yys_handler, win32con.HWND_NOTOPMOST, x_top,
                                  y_top, win_width, win_height,
                                  win32con.SWP_SHOWWINDOW)
        except Exception as error:
            self.display_msg('请确认你拥有管理员权限，否则无法重新设置大小，msg:{0}'.format(error))

        im_yys = pyautogui.screenshot(region=(x_top, y_top, win_width,
                                              win_height))
        self.display_msg('截图信息：{0},{1}'.format(
            (x_top, y_top, win_width, win_height), im_yys.mode))

        im = Image.open(self.filepath)
        times = 999
        for i in range(times):
            if self.stop:
                break

            im_yys = pyautogui.screenshot(region=(x_top, y_top, win_width,
                                                  win_height))

            loc = pyautogui.locate(im, im_yys, confidence=0.8)
            if loc is not None:
                self.display_msg('found: {0}, ({1},{2})'.format(
                    self.filename, x_top + loc.left, y_top + loc.top))
            else:
                self.display_msg('not found')
            time.sleep(1)
        self.display_msg('用户退出：正在退出')


class MatchWin(QMainWindow):
    stop_run = pyqtSignal()

    def __init__(self, parent=None):
        super(MatchWin, self).__init__(parent)
        self.ui = Ui_match_win()
        self.ui.setupUi(self)

        # 可以继承的初始化操作
        self.init_win()
        self.filepath = ''
        self.base_dir = r'F:\gitee\knowledge\yys_script\src\screenshot'

    def init_win(self):
        # 绑定信号和槽
        # self.ui.pbt_autocheck.clicked.connect(self.btn_autocheck_clicked)
        pass

    def show_attention(self, content):
        self.ui.te_explain.setText(content)

    def slot_btn_dir_clicked(self):
        self.filepath = os.path.abspath(self.ui.le_dir.text().strip())
        self.ui.le_dir.setText(self.filepath)
        dialog = QFileDialog(self.ui.centralwidget)
        # dialog.setFileMode(QFileDialog.Directory)
        # self.dir = dialog.getExistingDirectory(self, 'Open Directory', self.filepath)

        ret = dialog.getOpenFileName(self, 'open file', self.base_dir,
                                     "Png Files (*.png;*.jpg)")
        self.filepath = ret[0]
        self.filename = os.path.basename(self.filepath)
        self.display_msg('选中文件：{0}'.format(self.filename))

    def slot_btn_dir_released(self):
        self.ui.le_dir.setText(self.filepath)

    def slot_btn_start_clicked(self):
        self.auto_locate = AutoLocate(self, self.filepath)
        self.auto_locate.sendmsg.connect(self.display_msg)
        self.stop_run.connect(self.auto_locate.stop_run)
        self.has_start = True
        self.auto_locate.start()

    def slot_btn_stop_clicked(self):
        self.stop_run.emit()

    def display_msg(self, msg, type='Info'):
        if (type == 'Info'):
            '''输出日志到框内'''
            self.ui.te_log.moveCursor(QTextCursor.End)
            self.ui.te_log.insertPlainText(msg + '\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MatchWin()
    main_win.show()
    sys.exit(app.exec_())
