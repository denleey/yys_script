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
    1. 搜索 -> 御魂 -> 选择八歧大蛇 -> （挑战，悲鸣，，层）
    2. 单人挑战/（多人挑战，absent） -> 准备 -> p1 -> p2 -> p3
    3. 成功/失败 -> 领达摩奖励 -> 继续2
    4. (确认，默认邀请) -> （接受邀请，默认接受邀请）
注意事项：
    选择魂土： 选“悲” -> 没有“悲”时找层 -> 拖动之后 -> 选“悲”
'''

stages_prepare = [
    'search',
    'yuhun',
    'snake',
    'fight',
    'team_fight',
]

stages_loop = [
    'no_attention',
    'default_accept',
    'reward_accept',
    'yes',
    'accept',
    'team_fight',
    'prepare',
    'p3',
    'victory',
    'fail',
    'award',
    'fight',
    'p1',
    'p2',
]

yuhun_pics = [
    ['general', 'yuhun'],  # 选择第几层
    ['general', 'default_accept'],
    ['general', 'default_invite'],  # 默认邀请，通过 yes 和 default 来代替
    ['yuhun', 'snake'],
    ['yuhun', 'hun11'],
    ['yuhun', 'ten'],
    ['yuhun', 'tier'],
    ['yuhun', 'p1'],
    ['yuhun', 'p2'],
    ['yuhun', 'p3'],
]


class Yuhun(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(Yuhun, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()
        self.is_captain = self.config.get('captain', True)
        self.players = self.config.get('players', 2)
        self.select_tier = self.config.get('select_tier', 'hun11')
        self.total_times = self.config.get('total_times', 200)

        # 将图片打开成图像 ims
        self.pics = yuhun_pics
        self.pics.extend(self.basic_pics)
        self.pics.extend(self.team_pics)
        self.ims = screenshot.open_image_list(self.pics)

        # 队员不需要匹配挑战
        global stages_loop
        if self.is_captain is False:
            for key in ['team_fight', 'fight']:
                stages_loop.remove(key)

    def select_yuhun_tier(self, select_tier='hun11'):
        # 单个挑战 -> 选择魂土： 'hun11', 'ten', 'tier',
        im_yys = self.screenshot()
        loc = self.locate_im(self.ims[select_tier], im_yys)
        if loc:
            self.display_msg('点击：{0}进入下一步'.format('魂土'))
            self.click_loc_one(loc)
            time.sleep(0.5)
            return True

        loc = self.locate_im(self.ims['tier'], im_yys)
        if loc:
            self.display_msg('向下滑动到选择魂土')
            for i in range(2):
                self.move_loc_inc(loc.left, loc.top, 0.2)
                time.sleep(0.2)
                self.dragRel_loc_exact(0, -200, 1.0)
                time.sleep(1.0)

        # check again
        loc = self.locate_im(self.ims[select_tier])
        if loc:
            self.display_msg('点击：{0}进入下一步'.format('魂土'))
            self.click_loc_one(loc)
            time.sleep(0.5)
            return True

        return False

    def already_in_loop(self):
        for key in stages_loop:
            if self.locate_im(self.ims[key]):
                self.display_msg('当前状态：{0}，可进入loop'.format(key))
                if key == 'fight':
                    self.select_yuhun_tier(self.select_tier)
                return True
        return False

    def goto_loop(self):
        # 此处判断是否已经在循环，可以显著提高效率
        if self.already_in_loop():
            return True

        if self.is_captain is False:
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
            if key in ['search', 'yuhun', 'snake']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            elif key in ['fight', 'team_fight']:
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
                    time.sleep(0.5)  # 常规情况下，休眠0.5秒
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            if last_state != key:
                self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key

            if key == 'team_fight':
                need_wait_player = False
                if self.players == 3 and self.locate_im(self.ims['absent']):
                    need_wait_player = True
                elif self.players == 2:
                    # 检查中间的那个好友是否就绪
                    im_absent_box2 = self.screenshot_inc(500, 180, 150, 170)
                    if self.locate_im(self.ims['absent'], im_absent_box2):
                        need_wait_player = True

                if need_wait_player:
                    self.display_msg('等待队友到齐，如有队友退出请重选人数')
                    time.sleep(0.2)
                    continue
                else:
                    self.display_msg('点击：{0}进入下一步'.format(key))
                    self.click_loc_one(loc)

            elif key in ['fight', 'prepare']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                self.move_uncover(loc)

            elif key in ['p1', 'p2', 'p3']:
                if last_state != key:
                    self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))

            elif key in ['victory', 'fail', 'award']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'victory':
                    cur_loop_times += 1
                    self.display_msg('当前进度：{0}/{1}'.format(
                        cur_loop_times, self.total_times))
                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 2, 0.1)
                # 加快匹配的频率，不然会稍微便慢
                continue

            elif key == 'yes':
                loc_default = self.locate_im(self.ims['default'], im_yys)
                if loc_default:
                    # 成功之后的默认邀请，“默认”两个字前面的选中框
                    self.display_msg('设置为默认邀请队友')
                    self.click_loc_inc(loc_default.left - 24,
                                       loc_default.top + 11, 1)

                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            elif key == 'no_attention':
                self.click_loc_inc(loc.left - 22, loc.top + 15, 1)
                self.display_msg('点击：{0}进入下一步'.format(key))
                time.sleep(0.5)
                loc_tmp = self.locate_im(self.ims['yes'], im_yys)
                if loc_tmp:
                    self.display_msg('确认选中不再提示')
                    self.click_loc_one(loc_tmp)

            elif key in ['default_accept', 'accept', 'reward_accept']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            time.sleep(0.5)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'Yuhun'

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
    yuhun = Yuhun()
    yuhun.run()
