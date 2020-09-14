# -*- coding: utf-8 -*-

import time
import sys
import os
import logging
from random import randint, uniform
from PyQt5.QtCore import pyqtSignal
import pyautogui
import config
import screenshot
from autogui import AutoGui
'''
执行步骤：
    1. 搜索 -> 御灵 -> 选择类型 -> 选择层数 -> 挑战
    2. 挑战 -> 准备 -> 成功/失败 -> 领达摩奖励 -> 继续2
注意事项：
    可能同时存在的场景： （选择类型，选择层数，挑战）
'''

stages_prepare = [
    'search', 'yuling', 'dragon', 'fox', 'leopard', 'phenix', 'layer3', 'fight'
]
stages_loop = ['reward_accept', 'fight', 'prepare', 'victory', 'fail', 'award']

yuling_pics = [
    ['yuling', 'yuling'],  # 选择第几层
    ['yuling', 'layer3'],  # 选择第几层，可能与四种状态同时存在
    ['yuling', 'dragon'],  # 神龙
    ['yuling', 'fox'],  # 狐狸
    ['yuling', 'leopard'],  # 豹子
    ['yuling', 'phenix'],  # 凤凰
]


class Yuling(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(Yuling, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()

        # 将图片打开成图像 ims
        self.pics = yuling_pics
        self.pics.extend(self.basic_pics)
        self.ims = screenshot.open_image_list(self.pics)
        self.total_times = self.config.get('times', 200)

    def already_in_loop(self):
        for key in stages_loop:
            if self.locate_im(self.ims[key]):
                self.display_msg('当前状态：{0}，可进入loop'.format(key))
                loc_tmp = self.locate_im(self.ims['layer3'])
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format('layer3'))
                    self.click_loc_one(loc_tmp)
                return True
        return False

    def goto_loop(self):
        # 此处判断是否已经在循环，可以显著提高效率
        if self.already_in_loop():
            return True

        cur_check_times = 0
        last_state = ''
        layer3_reentry_times = 0
        while self.stop is False and cur_check_times < 20:
            cur_check_times += 1
            if cur_check_times % 5 == 0:
                self.display_msg('正在进行第{0}次尝试：'.format(cur_check_times))

            found = False
            key = ''
            im_yys = self.screenshot()
            for key in stages_prepare:
                loc = self.locate_im(self.ims[key], im_yys)
                if loc is not None:
                    found = True
                    break
            if found is False:
                # 此处判断是否已经在循环，可以增强稳定性
                if self.already_in_loop():
                    return True
                time.sleep(1)
                continue

            self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            if key in ['search', 'yuling']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
            elif key in ['dragon', 'fox', 'leopard', 'phenix']:
                # 说明当前已经进入到了选择类型的界面
                loc_tmp = None
                im_yys = self.screenshot()
                fight_type = self.config.get('type', 'leopard')
                if fight_type == 'dragon':
                    loc_tmp = self.locate_im(self.ims['dragon'], im_yys)
                elif fight_type == 'fox':
                    loc_tmp = self.locate_im(self.ims['fox'], im_yys)
                elif fight_type == 'leopard':
                    loc_tmp = self.locate_im(self.ims['leopard'], im_yys)
                elif fight_type == 'phenix':
                    loc_tmp = self.locate_im(self.ims['phenix'], im_yys)
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format(fight_type))
                    self.click_loc_one(loc_tmp)
                else:
                    self.display_msg('匹配不到状态：{0}'.format(fight_type))
            elif key == 'layer3':
                # 可重入2次确保可以点击成功
                if layer3_reentry_times < 1:
                    self.display_msg('点击：{0}进入下一步'.format('layer3'))
                    layer3_reentry_times += 1
                    self.click_loc_one(loc)
                else:
                    loc_tmp = self.locate_im(self.ims['fight'])
                    if loc_tmp:
                        # 说明当前已经进入到了选择类型的界面
                        self.display_msg('点击：{0}进入下一步'.format('fight'))
                        time.sleep(1)
                        return True
            last_state = key
            time.sleep(1)
        self.display_msg('未能进入到循环状态，正在退出')
        return False

    def loop(self):
        cur_loop_times = 0
        last_state = ''
        not_found_times = 0
        while self.stop is False and cur_loop_times < self.total_times:
            found = False
            key = ''
            im_yys = self.screenshot()
            # 此处要改成对应的loop结构体
            for key in stages_loop:
                loc = self.locate_im(self.ims[key], im_yys)
                if loc is not None:
                    found = True
                    break
            if found is False:
                not_found_times += 1
                if not_found_times > 100:
                    self.display_msg('超过100次未匹配，正在退出')
                    self.stop = True
                    break
                elif not_found_times > 30:
                    self.display_msg('未匹配到状态，休眠{0}秒'.format(not_found_times))
                    time.sleep(not_found_times)
                else:
                    time.sleep(1.5)  # 常规情况下，休眠1.5秒
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            # stages_loop = ['fight', 'prepare', 'victory', 'fail', 'award']
            self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key

            if key in ['fight', 'prepare']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                self.move_uncover(loc)

            elif key in ['victory', 'fail', 'award']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'award':
                    cur_loop_times += 1
                    self.display_msg('当前进度：{0}/{1}'.format(
                        cur_loop_times, self.total_times))
                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 2, 0.2)  # 点击两下显示更快
                time.sleep(0.5)
                continue

            elif key == 'reward_accept':
                self.click_loc_one(loc)
                self.display_msg('点击：{0}进入下一步'.format(key))

            time.sleep(1)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'Yuling'

        ret = self.get_window_handler()
        if ret is False:
            return

        ret = self.resize_win_size(1152, 679)
        # ret = self.resize_win_size()
        if ret is False:
            return

        if len(self.ims) == 0:
            self.display_msg('截图信息加载失败')
            return

        self.display_msg('正在尝试进入循环挑战状态')
        if self.goto_loop():
            self.loop()


if __name__ == '__main__':
    yuling = Yuling()
    yuling.run()
