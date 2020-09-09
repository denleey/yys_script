# -*- coding: utf-8 -*-

import time
import sys
import os
import logging
import win32gui
import win32con
from random import randint, uniform
from math import fabs
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow
import pyautogui
import config
import screenshot

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
# ui_path = os.path.abspath(cur_dir + os.path.sep + "..") + os.path.sep + 'ui'
ui_path = cur_dir + os.path.sep + 'ui'
sys.path.append(ui_path)

logging.basicConfig(
    level=logging.DEBUG,
    format=
    '%(asctime)s: [%(filename)s:line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d-%H:%M:%S',
    filename=None,
    filemode='match_width')

confidence = 0.8


class AutoGui(QThread):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(AutoGui, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()

        # 将图片打开成图像 ims
        self.pics = self.basic_pics
        self.ims = screenshot.open_image_list(self.pics)

    def init_attribute(self):
        '''不同派生类共同初始化的部分'''
        self.stop = False
        self.handler = None
        self.x_top = self.y_top = self.x_bottom = self.y_bottom = 0
        self.win_width = self.win_height = 0
        self.last_dis = 0

        # 基础功能用到的列表
        self.basic_pics = [
            ['general', 'search'],  # 搜索
            ['general', 'fight'],  # P0挑战，单人挑战
            ['general', 'prepare'],  # P1准备
            ['general', 'victory'],  # 结算胜利
            ['general', 'fail'],  # 结算失败
            ['general', 'award'],  # 结算时的达摩
            ['general', 'reward_accept'],  # 悬赏的邀请确认
            ['general', 'man'],  # 检查式神是否满级
        ]

        # 需要交换狗粮时用到的列表
        self.exchange_pics = [
            ['general', 'move'],  # 拖拉一段距离
            ['general', 'exchange'],  # 交换式神的交换
            ['role', 'all'],  # 选择全部
            ['role', 'fodder'],  # 选择素材
            ['role', 'ncard'],  # n卡
            ['role', 'rcard'],  # r卡
            ['role', 'flower'],  # 选择花
            # ['role', 'sr_card'],  # sr卡
            # ['role', 'ssr_card'],  # ssr卡
            # ['role', 'sp_card'],  # sp卡
        ]

        # 需要用到式神时用到的式神列表
        self.role_pics = [
            ['role', 'bianhua_ex'],  # 交换式神的界面
            ['role', 'bianhua_fight'],
            ['role', 'chaji'],  # 突破时的茶几
            ['role', 'chaji2'], # 突破时的茶几2
            ['role', 'yu_sp_fight1'],  # 战斗界面的玉藻前
            ['role', 'yu_sp_fight2'],  # 战斗界面的玉藻前
            ['role', 'yu_sp_ex1'],  # 交换式神界面的玉藻前
            ['role', 'yu_sp_ex2'],  # 交换式神界面的玉藻前
            ['role', 'yu_sp_ex3'],  # 交换式神界面的玉藻前
        ]

        # 锁定式神
        self.marked_pics = [
            ['role', 'marked'],
        ]

        # 组队挑战
        self.team_pics = [
            ['general', 'yes'],  # 确认
            ['general', 'default'],  # 默认两个字，配置yes，默认xx
            ['general', 'absent'],  # 组队界面制度的 + 字标识
            ['general', 'accept'],  # 队员默认接受邀请
            ['general', 'team_fight'],  # 组队时挑战会变得不一样
        ]

    def display_msg(self, msg):
        '''输出日志到框内'''
        self.sendmsg.emit(msg, 'Info')
        print(msg)

    def raise_msg(self, msg):
        '''输出日志到框内，且弹窗提醒错误'''
        self.sendmsg.emit(msg, 'Error')

    def clean_msg(self):
        '''清理日志输出框'''
        self.ui.pte_msg.clear()

    def stop_run(self):
        self.stop = True

    def get_window_handler(self):
        '''获取到阴阳师窗体信息'''
        handler = win32gui.FindWindow(0, self.win_name)  # 获取窗口句柄
        if handler == 0:
            self.raise_msg('捕获不到程序：' + self.win_name)
            return False
        self.handler = handler
        self.x_top, self.y_top, self.x_bottom, self.y_bottom = \
            win32gui.GetWindowRect(handler)
        self.win_width = self.x_bottom - self.x_top
        self.win_height = self.y_bottom - self.y_top
        self.display_msg('捕获到程序：{0},({1},{2}),{3},{4}'.format(
            self.win_name, self.x_top, self.y_top, self.win_width,
            self.win_height))

        logging.info(
            '位置信息：top({0},{1}), bottom({2},{3}), width:{4}, height:{5} '.
            format(self.x_top, self.y_top, self.x_bottom, self.y_bottom,
                   self.win_width, self.win_height))
        return True

    def resize_win_size(self, width=800, height=480):
        '''设置固定大小，方便后续截图和比对，这里比较有限制'''
        if self.handler is None or self.get_window_handler() is False:
            self.raise_msg('请确认程序有开启' + self.win_name)
            return False

        # reset win and update win info
        try:
            win32gui.SetWindowPos(self.handler, win32con.HWND_NOTOPMOST,
                                  self.x_top, self.y_top, width, height,
                                  win32con.SWP_SHOWWINDOW)
            self.get_window_handler()
        except Exception as error:
            self.raise_msg('请确认你拥有管理员权限，否则无法重新设置大小，msg:{0}'.format(error))
            return False
        return True

    def screenshot(self, x=0, y=0, w=0, h=0):
        '''默认截取yys整个页面，成功返回截图，失败返回None'''
        try:
            if x == 0 and y == 0 and w == 0 and h == 0:
                im = pyautogui.screenshot(region=(self.x_top, self.y_top,
                                                  self.win_width,
                                                  self.win_height))
            else:
                im = pyautogui.screenshot(region=(x, y, w, h))
            return im
        except Exception:
            # self.display_msg('截图失败：' + str(error))
            return None

    def screenshot_inc(self, x=0, y=0, w=0, h=0):
        '''默认截取yys相对位置，成功返回截图，失败返回None'''
        w = w if w != 0 else self.win_width
        h = h if h != 0 else self.win_height
        return self.screenshot(self.x_top + x, self.y_top + y, w, h)

    def locate_im(self, check_im, basic_im=None):
        '''检查图片是否存在, (Image, Image) -> loc or None'''
        try:
            if basic_im is None:
                im_yys = self.screenshot()
            else:
                im_yys = basic_im
            loc = pyautogui.locate(check_im, im_yys, confidence=confidence)
            return loc
        except Exception as error:
            self.display_msg('截图比对失败：' + str(error))
            return None

    def locate_im_exact(self, check_im, x, y, w, h):
        '''通过坐标来获取截图并查看图片是否存在'''
        try:
            im_yys = self.screenshot(x, y, w, h)
            loc = pyautogui.locate(check_im, im_yys, confidence=confidence)
            return loc
        except Exception as error:
            self.display_msg('截图比对失败：' + str(error))
            return None

    def locate_im_inc(self, check_im, x, y, w, h):
        '''通过坐标来获取截图并查看图片是否存在'''
        return self.locate_im_exact(check_im, self.x_top + x, self.y_top + y,
                                    w, h)

    def locate_ims(self, check_ims):
        '''检验一组图片截图是否在界面当中，存在时返回对应的 loc'''
        im_yys = self.screenshot()
        for im in check_ims:
            loc = self.locate_im(im, im_yys)
            if loc:
                return loc
        return None

    # %% 移动鼠标(0.5S)，取截图位置的偏中间位置，并触发鼠标点击，点击2次，间隔随机0-1S
    def click_loc(self, loc, times=-1):
        random_x = randint(10, loc.width - 10)
        random_y = randint(10, loc.height - 10)
        interval = uniform(0.2, 0.5)
        click_x = self.x_top + loc.left + random_x
        click_y = self.y_top + loc.top + random_y
        self.click_loc_exact(click_x, click_y, times, interval)

    def click_loc_exact(self, click_x, click_y, times=-1, interval=0.5):
        if times == -1:
            times = randint(2, 3)
        self.display_msg('点击位置：({0},{1},{2},{3})'.format(
            click_x, click_y, interval, times))
        pyautogui.click(click_x, click_y, times, interval, button='left')

    def click_loc_inc(self, inc_x, inc_y, times=-1, interval=0.5):
        return self.click_loc_exact(self.x_top + inc_x, self.y_top + inc_y,
                                    times, interval)

    def click_loc_one(self, loc):
        self.click_loc(loc, 1)

    def click_loc_twice(self, loc):
        self.click_loc(loc, 2)

    def move_uncover(self, loc):
        random_x = randint(-loc.width - loc.width, -loc.width)
        random_y = randint(-loc.height, loc.height)
        interval = uniform(0.1, 0.5)
        move_x = self.x_top + loc.left + random_x
        move_y = self.y_top + loc.top + random_y
        self.display_msg('偏移位置以防遮挡：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(move_x, move_y, duration=interval)

    def move_loc_exact(self, move_x, move_y, interval=0):
        interval = interval if interval != 0 else uniform(0.1, 0.5)
        self.display_msg('移动位置到：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(move_x, move_y, duration=interval)

    def move_loc_inc(self, move_x, move_y, interval=0):
        '''移动相对于主界面的相对位置'''
        interval = interval if interval != 0 else uniform(0.1, 0.5)
        self.display_msg('移动位置到：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(self.x_top + move_x,
                         self.y_top + move_y,
                         duration=interval)

    def scroll_loc_exact(self, clicks, move_x=0, move_y=0):
        '''滚动接口调用之后点击位置会不准
            clicks 参数表示滚动的格数。
            正数则页面向上滚动
            负数则向下滚动
        '''
        self.display_msg('滚动鼠标幅度：{0}'.format(clicks))
        pyautogui.scroll(clicks=clicks, x=move_x, y=move_y)

    def dragRel_loc_exact(self, x_offset, y_offset, du=0.5):
        '''
            @x_offset： 正数为按住一个点向右拖动，负数按住一个点向左拖动
            @y_offset： 正数为按住一个点向下拖动，负数按住一个点向上拖动，大小表示拖动幅度
            @du, 表示拖动使用的时间间隔滚动
        '''
        self.display_msg('拖动鼠标幅度：{0}, {1}'.format(x_offset, y_offset))
        pyautogui.dragRel(x_offset, y_offset, duration=du)

    def is_loc_marked_exact(self, x, y, w, h):
        return self.locate_im_exact(self.ims['marked'], x, y, w, h) is not None

    def is_loc_marked_inc(self, x, y, w, h):
        return self.locate_im_inc(self.ims['marked'], x, y, w, h) is not None

    def is_loc_man_exact(self, x, y, w, h):
        return self.locate_im_exact(self.ims['man'], x, y, w, h) is not None

    def is_loc_man_inc(self, x, y, w, h):
        return self.locate_im_inc(self.ims['man'], x, y, w, h) is not None

    def exchange_man_role_by_locs(self, role_locs, final_locs):
        ''' @function: 通过式神的相对位置和最终位置，将已经满级位置的式神更换为狗粮
            @role_locs: 需要检测的式神的相对位置[[x,y,w,h]]
            @final_locs: 要更换的狗粮的位置，即从哪个位置换一个狗粮上来，不同界面位置不同
            @注意事项：目前最多仅支持同时更换3只狗粮
        '''
        result = [0, 0, 0, 0, 0]
        for i in range(len(role_locs)):
            if self.is_loc_man_inc(role_locs[i][0], role_locs[i][1],
                                   role_locs[i][2], role_locs[i][3]):
                result[i] = 2

        self.display_msg('交换状态：{0}'.format(result))

        # 不存在满级式神时直接返回
        if 2 not in result:
            return result

        select_type = self.config.get('select_type', 'fodder')
        if select_type in ['ncard', 'fodder']:
            self.change_type(select_type)  # 切换到具体狗粮
            loc = self.locate_im(self.ims['move'])
            if loc:
                self.display_msg('拖动一段距离以获取更优的狗粮：{0}'.format(select_type))
                self.move_loc_inc(loc.left + 5, loc.top + 12)
                time.sleep(0.2)
                dis = randint(3, 5)
                self.last_dis = dis if self.last_dis != dis else dis + 1
                self.dragRel_loc_exact(self.last_dis, 0, 0.3)  #
                time.sleep(0.5)

        # 从狗粮列表的哪几个位置进行更换狗粮，因为不同界面，最终要换到的位置也不太一样
        exchange_locs = [[180, 440, 190, 205], [380, 440, 190, 205],
                         [640, 440, 190, 205]]
        for i in range(len(final_locs)):
            if result[i] != 2:
                continue
            loc_flower = self.locate_im_inc(self.ims['flower'],
                                            exchange_locs[i][0],
                                            exchange_locs[i][1],
                                            exchange_locs[i][2],
                                            exchange_locs[i][3])
            if loc_flower:
                start_x = exchange_locs[i][0] + loc_flower.left - 30
                start_y = exchange_locs[i][1] + loc_flower.top + 50
                self.move_loc_inc(start_x, start_y, 0.2)
                time.sleep(0.2)

                # 用最终位置减去最初的位置即可
                self.dragRel_loc_exact(final_locs[i][0] - start_x,
                                       final_locs[i][1] - start_y, 0.8)
                time.sleep(0.8)
            else:
                self.display_msg('没有找到合适的狗粮：{0}'.format(i))

        return result

    def change_type(self, select_type):
        types = [
            'all',
            'fodder',
            'ncard',
        ]
        types.remove(select_type)  # 去除是因为如果跟选择类型一致，就不用再切换
        im_yys = self.screenshot()
        for cur_type in types:
            # 点击任意一种匹配的类型，并点击进入切换界面
            loc = self.locate_im(self.ims[cur_type], im_yys)
            if loc is None:
                continue
            self.click_loc_one(loc)
            time.sleep(0.5)

            # 再选择对应需要选中的类型
            loc_tmp = self.locate_im(self.ims[select_type])
            if loc_tmp:
                self.display_msg('切换类型：{0}'.format(select_type))
                self.click_loc_one(loc_tmp)
                time.sleep(0.5)

    def run(self):
        pass
