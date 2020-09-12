# -*- coding: utf-8 -*-

import time
import sys
import os
import logging
from random import randint, uniform
from enum import Enum
from math import fabs
from PyQt5.QtCore import pyqtSignal
import pyautogui
import config
import screenshot
from autogui import AutoGui
'''
执行步骤：
    1. 搜索 -> 御魂 -> 业原火 -> 选择痴 -> 挑战
    2. 挑战 -> （检查满狗粮，交换，准备） -> 成功/失败 -> 领达摩奖励 -> 继续2
    3. 式神：彼岸花，更换狗粮
注意事项：
    选中狗粮模式才会更换狗粮
    彼岸花和火灵的铁鼠放在最左边的两个位置，好处是这两个位置可以不用检查是否满级，更换狗粮时也不考虑，省了很多时间

'''

stages_prepare = [
    'search',
    'yuhun',
    'huo',
    'chi',
    'fight',
]
stages_loop = [
    'reward_accept', 'fight', 'check_man', 'exchange', 'all', 'p1', 'p2', 'p3',
    'victory', 'fail', 'award'
]

chi_pics = [
    ['general', 'yuhun'],
    ['chi', 'chi'],
    ['chi', 'check_man'],
    ['chi', 'huo'],
    ['chi', 'p1'],
    ['chi', 'p2'],
    ['chi', 'p3'],
    ['role', 'marked'],
]


class Chi(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(Chi, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.fight_type = config.get('type', 'fodder')  # 0非狗粮，1N卡狗粮，2白蛋狗粮
        self.ex_fodder = config.get('ex_fodder', True)
        self.init_attribute()

        # 将图片打开成图像 ims
        self.pics = chi_pics.copy()
        self.pics.extend(self.basic_pics)
        self.pics.extend(self.exchange_pics)
        self.ims = screenshot.open_image_list(self.pics)

    def already_in_loop(self):
        for key in stages_loop:
            if self.locate_im(self.ims[key]):
                self.display_msg('当前状态：{0}，可进入loop'.format(key))
                loc_tmp = self.locate_im(self.ims['chi'])
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format('chi'))
                    self.click_loc_one(loc_tmp)
                return True
        return False

    def get_fodder_status(self):
        '''
            @function: 检测3，4，5位置的式神满级情况
            @return: [x,x,x]，0未满级，1输出式神满级，2狗粮满级
        '''
        result = [0, 0, 0]

        # 另外两个位置1和2： [75, 350, 190, 140], [245, 310, 1150, 500]
        man_locs = [[445, 340, 190, 180], [645, 340, 160, 170],
                    [805, 320, 230, 120]]
        for i in range(len(man_locs)):
            if self.is_loc_man_inc(man_locs[i][0], man_locs[i][1],
                                   man_locs[i][2], man_locs[i][3]):
                result[i] = 2
        return result

    def get_exchange_fodder_status(self):
        '''
            @role_locs: [[x,x,x,x]]，表示式神的位置的数组
            @final_locs: [[x,y],[x,y]]，表示最终要移动到哪个式神位置
            @return: [x,x,x]，更换式神的情况，0未更换，1输出式神未更换，2表示更换了
        '''
        # 另外两个位置： , [701, 150, 250, 230]]
        role_locs = [[0, 150, 185, 230], [185, 150, 250, 230],
                     [445, 150, 250, 230]]
        # 中间位置用白蛋的话可能有点问题，适当调低
        final_locs = [[75, 350], [425, 350], [565, 350]]

        return self.exchange_man_role_by_locs(role_locs, final_locs)

    def goto_loop(self):
        # 此处判断是否已经在循环，可以显著提高效率
        if self.already_in_loop():
            return True

        cur_check_times = 0
        last_state = ''
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
            if key in ['search', 'yuhun', 'huo']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            if key == 'chi':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                return True

            last_state = key
            time.sleep(1)
        self.display_msg('未能进入到循环状态，正在退出')
        return False

    def loop(self):
        total_times = self.config.get('total_times', 200)
        cur_loop_times = 0
        last_state = ''
        not_found_times = 0
        while self.stop is False and cur_loop_times < total_times:
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
                    time.sleep(1)  # 常规情况下，休眠1.5秒
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            # stages_loop = ['fight', 'prepare', 'victory', 'fail', 'award']
            if last_state != key:
                self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key

            if key in ['fight']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                self.move_uncover(loc)

            elif key == 'check_man':
                # 是否要更新狗粮
                if self.ex_fodder is False:
                    loc_tmp = self.locate_im(self.ims['prepare'], im_yys)
                    if loc_tmp:
                        self.display_msg('点击：{0}进入下一步'.format('prepare'))
                        self.click_loc_one(loc_tmp)
                        self.move_uncover(loc_tmp)
                    continue

                # 查检是否需要更换狗粮
                status = self.get_fodder_status()
                self.display_msg('状态：{0}，狗粮状态：{1}'.format('check_man', status))
                if 2 in status and (status.count(2) + status.count(1)) > 0:
                    # 点击进入切换狗粮界面
                    self.click_loc_exact(self.x_top + 340, self.y_top + 465, 1)
                else:
                    loc_tmp = self.locate_im(self.ims['prepare'])
                    if loc_tmp:
                        self.display_msg('无需换狗粮，点击：{0}进入下一步'.format('prepare'))
                        self.click_loc_one(loc_tmp)

            elif key in ['exchange', 'all']:
                # 组队时队员没有 exchange
                result = self.get_exchange_fodder_status()
                self.display_msg('共更换了{}只狗粮'.format(result.count(2)))
                loc_tmp = self.locate_im(self.ims['prepare'])
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format('prepare'))
                    self.click_loc_one(loc_tmp)
                continue

            elif key in ['p1', 'p2', 'p3']:
                time.sleep(1.5)

            elif key in ['victory', 'fail', 'award']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'victory':
                    cur_loop_times += 1
                    self.display_msg('当前进度：{0}/{1}'.format(
                        cur_loop_times, total_times))
                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 2, 0.2)  # 点击两下显示更快
                time.sleep(0.5)
                continue

            elif key == 'reward_accept':
                self.click_loc_one(loc)
                self.display_msg('点击：{0}进入下一步'.format(key))

            time.sleep(0.8)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'Chi'

        ret = self.get_window_handler()
        if ret is False:
            return

        ret = self.resize_win_size(1152, 679)
        if ret is False:
            return

        if len(self.ims) == 0:
            self.display_msg('截图信息加载失败')
            return

        self.display_msg('正在尝试进入循环挑战状态')
        if self.goto_loop():
            self.loop()


if __name__ == '__main__':
    chi = Chi()
    chi.run()
