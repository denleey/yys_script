# -*- coding: utf-8 -*-

import time
import sys
import os
import threading
import datetime
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
# ui_path = os.path.abspath(cur_dir + os.path.sep + "..") + os.path.sep + 'ui'
ui_path = cur_dir + os.path.sep + 'ui'
images_path = cur_dir + os.path.sep + 'screenshot'
sys.path.append(ui_path)
sys.path.append(images_path)

from main_widget import Ui_yys_win
from yuhun import Yuhun
from chi import Chi
from yuling import Yuling
from chapter import Chapter
from chapter_captain import ChapterCaptain
from yysbreak import YysBreak
import images
import config


class YysWin(QMainWindow):
    stop_run = pyqtSignal()

    def __init__(self, parent=None, win_name='阴阳师-网易游戏'):
        super(YysWin, self).__init__(parent)
        self.ui = Ui_yys_win()
        self.ui.setupUi(self)

        # 可以继承的初始化操作
        self.init_win()

    def init_win(self):
        self.ui.pte_msg.clear()
        self.has_start = False
        self.select_fun = self.ui.cb_fuctions.currentText()
        self.show_attention(config.general['attention'])
        self.setWindowTitle(config.general['title'])
        self.setWindowIcon(QIcon(":/icon/images/zhangliang.ico"))
        self.ui.lb_qrcode.setPixmap(QPixmap(":/images/images/qun.jpg"))

        # 绑定信号和槽
        self.ui.pbt_autocheck.clicked.connect(self.btn_autocheck_clicked)

        # self.pbt_start.clicked.connect(yys_win.btn_start_clicked)
        # self.pushButton.clicked.connect(yys_win.btn_stop_clicked)
        # self.pbt_restart.clicked.connect(yys_win.btn_restart_clicked)
        # self.cb_fuctions.currentIndexChanged['QString'].connect(yys_win.cb_functions_index_changed)
        # self.cb_p1.currentIndexChanged['QString'].connect(yys_win.cb_p1_index_changed)
        # self.cb_p2.currentIndexChanged['QString'].connect(yys_win.cb_p2_index_changed)
        # self.cb_p3.currentIndexChanged['QString'].connect(yys_win.cb_p3_index_changed)
        # self.cb_p4.currentIndexChanged['QString'].connect(yys_win.cb_p4_index_changed)
        # self.cb_p5.currentIndexChanged['QString'].connect(yys_win.cb_p5_index_changed)
        # self.cb_p6.currentIndexChanged['QString'].connect(yys_win.cb_p6_index_changed)
        # self.ptn_clear.clicked.connect(self.pte_msg.clear)

        # 认证
        self.expired = True
        self.check_license()

    def display_msg(self, msg, type='Info'):
        if (type == 'Info'):
            '''输出日志到框内'''
            self.ui.pte_msg.moveCursor(QtGui.QTextCursor.End)
            self.ui.pte_msg.insertPlainText(msg + '\n')
        else:
            self.raise_msg(msg)

    def raise_msg(self, msg):
        '''输出日志到框内，且弹窗提醒错误'''
        self.display_msg(msg + '\n')

    def clean_msg(self):
        '''清理日志输出框'''
        self.ui.pte_msg.clear()

    def set_ui_cmbox(self, cb, lines):
        # type: combox, [str]
        cb.clear()
        cb.addItems(lines)

    def cb_functions_index_changed(self):
        self.select_fun = self.ui.cb_fuctions.currentText()
        if self.select_fun == '御魂':
            self.show_attention(config.yuhun['attention'])
            # 根据功能调整参数的列表
            self.set_ui_cmbox(self.ui.cb_p1, ['单人', '双人', '三人'])
            self.set_ui_cmbox(self.ui.cb_p2, ['队长', '队员'])
            self.set_ui_cmbox(self.ui.cb_p3, ['可能翻车', '不会翻车'])
            self.set_ui_cmbox(self.ui.cb_p4, ['挂机次数', '100', '200', '400'])
            self.set_ui_cmbox(self.ui.cb_p5, ['魂十一', '魂十'])
            self.set_ui_cmbox(self.ui.cb_p6, ['参数6'])
        elif self.select_fun == '困28':
            self.show_attention(config.chapter['attention'])
            self.set_ui_cmbox(self.ui.cb_p1, ['单人', '双人'])
            self.set_ui_cmbox(self.ui.cb_p2, ['队长', '队员'])
            self.set_ui_cmbox(self.ui.cb_p3,
                              ['挂机次数', '100', '200', '400', '9999'])
            self.set_ui_cmbox(self.ui.cb_p4, ['谁带输出', '队长', '队员'])
            self.set_ui_cmbox(self.ui.cb_p5, ['狗粮类型', 'N卡', '白蛋'])
            self.set_ui_cmbox(self.ui.cb_p6, ['参数6'])
        elif self.select_fun == '御灵':
            self.show_attention(config.yuling['attention'])
            self.set_ui_cmbox(self.ui.cb_p1,
                              ['挑战类型', 'dragon', 'fox', 'leopard', 'phenix'])
            self.set_ui_cmbox(self.ui.cb_p2, ['层数', '3', '2', '1'])
            self.set_ui_cmbox(self.ui.cb_p3,
                              ['挂机次数', '100', '200', '400', '9999'])
            self.set_ui_cmbox(self.ui.cb_p4, ['狗粮类型', 'N卡', '白蛋'])
            self.set_ui_cmbox(self.ui.cb_p4, ['参数4'])
            self.set_ui_cmbox(self.ui.cb_p5, ['参数5'])
            self.set_ui_cmbox(self.ui.cb_p6, ['参数6'])
        elif self.select_fun == '业原火':
            self.show_attention(config.yeyuanhuo['attention'])
            self.set_ui_cmbox(self.ui.cb_p1, ['层数', '3', '2', '1'])
            self.set_ui_cmbox(self.ui.cb_p2,
                              ['挂机次数', '100', '200', '400', '9999'])
            self.set_ui_cmbox(self.ui.cb_p3, ['快速', '花带狗粮'])
            self.set_ui_cmbox(self.ui.cb_p4, ['狗粮类型', 'N卡', '白蛋'])
            self.set_ui_cmbox(self.ui.cb_p5, ['参数5'])
            self.set_ui_cmbox(self.ui.cb_p6, ['参数6'])
        elif self.select_fun == '结界突破':
            self.show_attention(config.yys_break['attention'])
            self.set_ui_cmbox(self.ui.cb_p1, ['参数1'])
            self.set_ui_cmbox(self.ui.cb_p2, ['参数2'])
            self.set_ui_cmbox(self.ui.cb_p3, ['参数3'])
            self.set_ui_cmbox(self.ui.cb_p4, ['参数4'])
            self.set_ui_cmbox(self.ui.cb_p5, ['参数5'])
            self.set_ui_cmbox(self.ui.cb_p6, ['参数6'])

    def get_config_from_param_cb(self):
        p1 = self.ui.cb_p1.currentText()
        p2 = self.ui.cb_p2.currentText()
        p3 = self.ui.cb_p3.currentText()
        p4 = self.ui.cb_p4.currentText()
        p5 = self.ui.cb_p5.currentText()
        # p6 = self.ui.cb_p6.currentText()

        if self.select_fun == '御魂':
            if p1 == '双人':
                config.yuhun['players'] = 2
            elif p1 == '单人':
                config.yuhun['players'] = 1
            else:
                config.yuhun['players'] = 3

            config.yuhun['captain'] = True
            if p2 == '队员':
                config.yuhun['captain'] = False

            config.yuhun['may_fail'] = False
            if p3 == '可能翻车':
                config.yuhun['may_fail'] = True

            config.yuhun['times'] = 9999
            if p4 == '100':
                config.yuhun['times'] = 100
            elif p4 == '200':
                config.yuhun['times'] = 200
            elif p4 == '400':
                config.yuhun['times'] = 400

            config.yuhun['select_tier'] = 'hun11'
            if p5 == '魂十':
                config.yuhun['select_tier'] = 'ten'

        elif self.select_fun == '困28':
            if p1 == '双人':
                config.chapter['players'] = 2
            elif p1 == '单人':
                config.chapter['players'] = 1

            config.chapter['captain'] = True
            if p2 == '队员':
                config.chapter['captain'] = False

            config.chapter['times'] = 9999
            if p3 == '100':
                config.chapter['times'] = 100
            elif p3 == '200':
                config.chapter['times'] = 200
            elif p3 == '400':
                config.chapter['times'] = 400

            config.chapter['captain_output'] = False
            if p4 == '队长':
                config.chapter['captain_output'] = True

            config.chapter['role'] = 'yu'  # p4
            config.chapter['select_type'] = 'fodder'  # p5
            if p5 == 'N卡':
                config.chapter['select_type'] = 'ncard'

        elif self.select_fun == '御灵':
            config.yuling['type'] = 'leopard'
            if p1 == 'dragon':
                config.yuling['type'] = 'dragon'
            elif p1 == 'fox':
                config.yuling['type'] = 'fox'
            elif p1 == 'phenix':
                config.yuling['type'] = 'phenix'

            config.yuling['layer'] = 3
            if p2 == '2':
                config.yuling['layer'] = 2
            elif p2 == '1':
                config.yuling['layer'] = 1

            config.yuling['times'] = 9999
            if p3 == '100':
                config.yuling['times'] = 100
            elif p3 == '200':
                config.yuling['times'] = 200
            elif p3 == '400':
                config.yuling['times'] = 400

        elif self.select_fun == '业原火':
            config.yeyuanhuo['layer'] = 3
            if p1 == '2':
                config.yeyuanhuo['layer'] = 2
            elif p2 == '1':
                config.yeyuanhuo['layer'] = 1

            config.yeyuanhuo['times'] = 200
            if p2 == '100':
                config.yeyuanhuo['times'] = 100
            elif p2 == '400':
                config.yeyuanhuo['times'] = 400

            config.yeyuanhuo['ex_fodder'] = False
            if p3 == '快速':
                config.yeyuanhuo['ex_fodder'] = False
            elif p3 == '花带狗粮':
                config.yeyuanhuo['ex_fodder'] = True

            config.yeyuanhuo['select_type'] = 'fodder'  # p5
            if p4 == 'N卡':
                config.yeyuanhuo['select_type'] = 'ncard'

    def cb_p1_index_changed(self):
        # self.display_msg('cb_p1_index_changed\n')
        pass

    def cb_p2_index_changed(self):
        # self.display_msg('cb_p2_index_changed\n')
        pass

    def cb_p3_index_changed(self):
        # self.display_msg('cb_p3_index_changed\n')
        pass

    def cb_p4_index_changed(self):
        # self.display_msg('cb_p4_index_changed\n')
        pass

    def cb_p5_index_changed(self):
        # self.display_msg('cb_p5_index_changed\n')
        pass

    def cb_p6_index_changed(self):
        # self.display_msg('cb_p6_index_changed\n')
        pass

    def check_license(self):
        '''设置过期时间'''
        today = datetime.date.today()
        expire_time = datetime.date(2020, 10, 8)
        if today > expire_time:
            self.display_msg('认证已过期')
        else:
            self.expired = False
            self.display_msg('还有{0}天过期'.format(expire_time - today))

    def btn_autocheck_clicked(self):
        self.display_msg('自动挂机检测：{0}'.format(
            self.ui.cb_fuctions.currentText()))
        self.stop_run.emit()

    def btn_restart_clicked(self):
        self.btn_stop_clicked()
        self.btn_start_clicked()

    def btn_stop_clicked(self):
        self.display_msg('停止挂机：{0}'.format(self.select_fun))
        self.has_start = False
        self.stop_run.emit()
        self.show_attention(config.general['attention'] + '\n' +
                            config.general['version'])

    def btn_start_clicked(self):
        # 从参数列表中选择参数
        self.get_config_from_param_cb()

        if self.expired is True:
            self.display_msg('认证已经过期，即将退出...')
            return

        if self.has_start is True:
            self.display_msg('挂机已启动，请务重新启动，{0}' + self.select_fun)
            return

        self.display_msg('启动挂机：{0}'.format(self.select_fun))
        if self.select_fun == '御魂':
            self.display_msg('参数：{0}'.format(config.yuhun.items()))
            self.yuhun = Yuhun(self, config.yuhun)
            self.yuhun.sendmsg.connect(self.display_msg)
            self.stop_run.connect(self.yuhun.stop_run)
            self.has_start = True
            self.yuhun.start()
        elif self.select_fun == '御灵':
            self.display_msg('参数：{0}'.format(config.yuling.items()))
            self.yuling = Yuling(self, config.yuling)
            self.yuling.sendmsg.connect(self.display_msg)
            self.stop_run.connect(self.yuling.stop_run)
            self.has_start = True
            self.yuling.start()
        elif self.select_fun == '业原火':
            self.display_msg('参数：{0}'.format(config.yeyuanhuo.items()))
            self.chi = Chi(self, config.yeyuanhuo)
            self.chi.sendmsg.connect(self.display_msg)
            self.stop_run.connect(self.chi.stop_run)
            self.has_start = True
            self.chi.start()
        elif self.select_fun == '困28':
            self.display_msg('参数：{0}'.format(config.chapter.items()))
            self.is_captain = config.chapter.get('captain', True)
            if self.is_captain:
                self.chapter = ChapterCaptain(self, config.chapter)
            else:
                self.chapter = Chapter(self, config.chapter)
            self.chapter.sendmsg.connect(self.display_msg)
            self.stop_run.connect(self.chapter.stop_run)
            self.has_start = True
            self.chapter.start()
        elif self.select_fun == '结界突破':
            self.display_msg('结界突破不设置参数')
            self.yysbreak = YysBreak(self)
            self.yysbreak.sendmsg.connect(self.display_msg)
            self.stop_run.connect(self.yysbreak.stop_run)
            self.has_start = True
            self.yysbreak.start()

    def show_attention(self, contenet):
        self.ui.te_attention.setText(contenet + '\n开源地址：' +
                                     config.general['gitpath'] + '\n版本信息：' +
                                     config.general['version'])
