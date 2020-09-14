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
    1. 海国 -> 幻境间隙 -> 暝灯 -> 暝灯（点亮） -> 挑战
    2. 挑战 -> 准备 -> 成功/失败 -> 领达摩奖励 -> 继续2
注意事项：

'''

stages_prepare = [
    'haiguo', 'mingdeng', 'mingdeng_clicked', 'huanjing', 'main_return'
]
stages_loop = ['reward_accept', 'activity_fight', 'prepare', 'victory', 'fail', 'award']

activity_pics = [
    ['general', 'main_return'],  # 返回
    ['general', 'reward_accept'],  # 接受奖励
    ['general', 'prepare'],  # 接受奖励
    ['general', 'victory'],  # 接受奖励
    ['general', 'award'],  # 接受奖励
    ['general', 'prepare'],  # 接受奖励
    ['activity', 'haiguo'],  # 海国
    ['activity', 'huanjing'],  #
    ['activity', 'mingdeng'],  # 未点击的暝灯
    ['activity', 'mingdeng_clicked'],  # 已经点击的暝灯
    ['activity', 'activity_fight'],  # 挑战（因字体跟通用的挑战不同）
    ['activity', 'not_enough'],  # 挑战（因字体跟通用的挑战不同）
]


class Activity(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(Activity, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()

        # 将图片打开成图像 ims
        self.pics = activity_pics
        self.pics.extend(self.basic_pics)
        self.ims = screenshot.open_image_list(self.pics)
        self.total_times = self.config.get('total_times', 20)

    def already_in_loop(self):
        for key in stages_loop:
            if self.locate_im(self.ims[key]):
                self.display_msg('当前状态：{0}，可进入loop'.format(key))
                return True
        return False

    def goto_loop(self):
        # 此处判断是否已经在循环，可以显著提高效率
        if self.already_in_loop():
            return True

        global stages_prepare
        cur_check_times = 0
        last_state = ''
        already_remove_return = False
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
            if key in ['haiguo', 'huanjing', 'mingdeng']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                if already_remove_return is False:
                    stages_prepare.remove('main_return')
                    already_remove_return = True

            if key == 'main_return':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                self.move_uncover(loc)
                stages_prepare.remove('main_return')

            elif key == 'mingdeng_clicked':
                '''点击暝灯说明已经可以进入循环了'''
                self.display_msg('点击：{0}进入下一步'.format(key))
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
                elif not_found_times > 60:
                    self.display_msg('未匹配到状态，休眠{0}秒'.format(not_found_times))
                    time.sleep(not_found_times)
                else:
                    time.sleep(1.5)  # 常规情况下，休眠1.5秒
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key

            if key == 'activity_fight':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                self.move_uncover(loc)
                time.sleep(0.2)
                loc_tmp = self.locate_im(self.ims['not_enough'])
                if loc_tmp:
                    self.display_msg('今日挑战次数已经用完,正在退出')
                    self.stop = True
                    continue

            elif key == 'prepare':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                self.move_uncover(loc)

            elif key in ['victory', 'fail', 'award']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 2, 0.2)  # 点击两下显示更快
                time.sleep(0.5)
                if key == 'award':
                    time.sleep(0.5)
                    cur_loop_times += 1
                    self.display_msg('当前进度：{0}/{1}'.format(
                        cur_loop_times, self.total_times))
                continue

            elif key == 'reward_accept':
                self.click_loc_one(loc)
                self.display_msg('点击：{0}进入下一步'.format(key))

            time.sleep(1)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'Activity'

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
    activity = Activity()
    activity.run()
