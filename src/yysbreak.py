# -*- coding: utf-8 -*-

import time
import sys
import os
import logging
from random import randint, uniform
from enum import Enum
from PyQt5.QtCore import pyqtSignal
import pyautogui
import config
import screenshot
from autogui import AutoGui
'''
执行步骤：
    1. 搜索 -> 结界突破 -> 个人防守记录 -> （寮防守记录，解锁） -> （个人防守记录，解锁
    2. （个人防守记录，解锁） -> 识别个人3*3
    3. （破，败）-> 挑战 -> (准备) -> 锁定式神（已方，敌方）
    4. （额外的奖励，点击屏幕继续）
    5. -> 成功/失败 -> 领达摩奖励 -> 继续2

注意事项：
    挑战顺序：
        寮 -> 个人 -> 结束
    锁定第4个位置的式神
    个人结束标志：没有挑战券或者是遇到一次失败
    寮挑战结束标示：8个图全部挑战失败
'''

stages_prepare = ['search', 'break', 'record']
stages_loop = [
    'click_to_continue',
    'no_ticket',
    'break_fight',
    'record',
    'prepare',
    'victory',
    'fail',
    'award',  # 常规挑战
]

break_pics = [
    ['general', 'click_to_continue'],
    ['break', 'break'],  # 突破界面
    ['break', 'record'],
    ['break', 'person'],  # 切换模式
    ['break', 'group'],  # 切换模式
    ['break', 'break_failed'],  # 失败，折箭
    ['break', 'breaked'],  # 破
    ['break', 'over'],  # 0/ 30次或者6次机会用完了
    ['break', 'break_fight'],
    ['break', 'no_ticket'],
]


class YysBreak(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(YysBreak, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()

        # 将图片打开成图像 ims
        self.pics = break_pics
        self.pics.extend(self.basic_pics)
        self.pics.extend(self.role_pics)
        self.pics.extend(self.marked_pics)
        self.ims = screenshot.open_image_list(self.pics)
        self.auto_mark = config.get('auto_mark', True)

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
            last_state = key
            if key in ['search', 'break']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
            elif key in ['record']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                return True
            time.sleep(0.8)
        self.display_msg('未能进入到循环状态，正在退出')
        return False

    def change_team(self, status):
        self.display_msg('替换队伍')

    def loop(self):
        cur_loop_times = 0
        last_state = ''
        not_found_times = 0
        already_fight_group = False
        already_fight_person = False
        last_group_fight_index = 0
        cur_type = 'person'  # 初始时将类型设定为个人挑战
        role_locked = False

        # 个人挑战的九宫格的 （x_top, y_top, w, h）
        self.person_boxes = [
            [190, 150, 270, 90],
            [190, 260, 270, 90],
            [190, 370, 270, 90],
            [480, 150, 270, 90],
            [480, 260, 270, 90],
            [480, 370, 270, 90],
            [760, 150, 270, 90],
            [760, 260, 270, 90],
            [760, 370, 270, 90],
        ]

        # 寮挑战的 2*4 格子
        self.group_boxes = [
            [440, 150, 270, 90],
            [440, 250, 270, 90],
            [440, 350, 270, 90],
            [440, 450, 270, 90],
            [730, 150, 270, 90],
            [730, 250, 270, 90],
            [730, 350, 270, 90],
            [730, 450, 270, 90],
        ]

        while self.stop is False:
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
                elif not_found_times > 40:
                    # 打得比较慢的时候，是有可能超过1分钟的
                    self.display_msg('未匹配到状态，休眠{0}秒'.format(10))
                    time.sleep(10)
                else:
                    time.sleep(1.5)  # 常规情况下，休眠1.5秒
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key
            if key == 'record' and cur_type == 'group':
                '''组队挑战'''
                if self.locate_im(self.ims['over']):
                    '''当出现0/6时，说明已经全部挑战完了'''
                    already_fight_group = True

                if already_fight_group:
                    loc_tmp = self.locate_im(self.ims['person'], im_yys)
                    if loc_tmp:
                        self.display_msg('点击：{0}进入下一步'.format('个人突破'))
                        self.click_loc_one(loc_tmp)
                        last_group_fight_index = 0
                        cur_type = 'person'
                        time.sleep(1.0)
                    continue

                boxes = self.group_boxes
                if last_group_fight_index < len(boxes):
                    im_box = self.screenshot_inc(
                        boxes[last_group_fight_index][0],
                        boxes[last_group_fight_index][1],
                        boxes[last_group_fight_index][2],
                        boxes[last_group_fight_index][3])
                    '''遇到已经挑战成功的单位，说明寮全部挑战完成'''
                    if self.locate_im(self.ims['breaked'], im_box):
                        already_fight_group = True
                        continue
                    '''跳过已经挑战失败的单位'''
                    if self.locate_im(self.ims['break_failed'], im_box):
                        last_group_fight_index += 1
                    self.display_msg(
                        '正在挑战第{0}个怪'.format(last_group_fight_index))
                    self.click_loc_inc(boxes[last_group_fight_index][0] + 200,
                                       boxes[last_group_fight_index][1] + 30,
                                       1)
                else:
                    '''如果2*4的最后一个怪也挑战失败了，说明寮突破也就可以结束了'''
                    already_fight_group = True
                    self.display_msg(
                        '第{0}个怪都挑战失败了'.format(last_group_fight_index))

            elif key == 'record' and cur_type == 'person':
                '''个人挑战，寮挑战未进行时切先换成寮挑战'''
                if already_fight_group is False:
                    self.display_msg('先进行寮突破')
                    loc_tmp = self.locate_im(self.ims['group'], im_yys)
                    if loc_tmp:
                        self.display_msg('点击：{0}进入下一步'.format('寮突破'))
                        self.click_loc_one(loc_tmp)
                        last_group_fight_index = 0
                        cur_type = 'group'
                        time.sleep(0.8)
                    continue

                # 每次都都从0开始，保证
                boxes = self.person_boxes
                i = 0
                for i in range(0, len(boxes)):
                    im_box = self.screenshot_inc(boxes[i][0], boxes[i][1],
                                                 boxes[i][2], boxes[i][3])
                    '''忽略已经挑战过且成功的格子'''
                    if self.locate_im(self.ims['breaked'], im_box):
                        continue
                    '''跳过已经挑战失败的单位，当是最后一个式神失败时，认为可以结束了'''
                    if self.locate_im(self.ims['break_failed'], im_box):
                        continue

                    self.display_msg('正在挑战第{0}个怪'.format(i + 1))
                    self.click_loc_inc(boxes[i][0] + 200, boxes[i][1] + 30, 1)
                    time.sleep(0.8)  # 等待挑战界面出来
                    break

                if i == len(boxes):
                    '''说明九宫格可以挑战的都挑战完了'''
                    self.display_msg('最后一个格子挑战失败，退出')
                    self.stop = True

            elif key in ['break_fight']:
                if already_fight_person:
                    self.display_msg('没有挑战券了，结束当前挑战')
                    self.click_loc_inc(loc.left, loc.top + 60, 1)
                    return

                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                time.sleep(0.2)  # 为了识别到没有挑战券了，睡眠时间要短
                continue

            elif key == 'prepare':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                time.sleep(1.0)
                if self.auto_mark is False:
                    continue
                '''锁定式神，锁定第四个位置'''
                if (role_locked is False
                        and self.is_loc_man_inc(645, 340, 160, 170)) is False:
                    self.display_msg('点击锁定第四个位置进入下一步')
                    self.click_loc_inc(725, 440, 1)
                    self.move_uncover(loc)
                else:
                    self.display_msg('{0}已经锁定'.format(key))
                    role_locked = True

            elif key in ['victory', 'fail', 'award']:
                '''寮突破失败时继续挑战下一个，个人突破时每次都从第一个开始检查'''
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'victory':
                    cur_loop_times += 1
                    self.display_msg('当前完成次数：{0}'.format(cur_loop_times))
                elif cur_type == 'group' and key == 'fail':
                    last_group_fight_index += 1

                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 2, 0.2)

            elif key == 'click_to_continue':
                '''挑战3，6，9个时会开箱子，开箱子时要点击不会触发其他功能的位置'''
                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 1)

            elif key == 'no_ticket':
                already_fight_person = True
                self.display_msg('所有挑战完成，正在退出')

            time.sleep(0.8)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'break'

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
    yysbreak = YysBreak()
    yysbreak.run()
