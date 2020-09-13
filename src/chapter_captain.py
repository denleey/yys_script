# -*- coding: utf-8 -*-

import time
import sys
import os
import logging
from random import randint, uniform
from math import fabs
from PyQt5.QtCore import pyqtSignal
import pyautogui
import config
import screenshot
from autogui import AutoGui
from datetime import datetime
'''
困28队长

单人执行步骤：
    1. 搜索 -> 困28 -> 选择困难（hard，not_hard） -> 探索
        1.1 邀请最近的一个队友进行进行挑战（可能不用）
            （创建队伍，探索） -> （创建，不公开） -> （缺席，组队挑战）
        1.2 默认邀请队友继续挑战
    2. 困28 -> 探索 ->  挑战（fight, boss_fight, 解除锁定）-> 拖拉界面
        -> 检查狗粮满的界面（准备，满, check_man）
        -> 换狗粮（满，素材，交换，全部，白蛋（第4只开始），准备，输出）
        -> 成功/失败 -> 达摩领取奖励 -> 小纸人（盒子） -> 奖励确认（奖励框正文某处）
    3. 准备
注意事项：
    可能点击到观战，做了容错
'''

stages_prepare = ['search', '28', 'probe']  # 没有必要去确认循环了

stages_loop = [
    'yes',  # 确认邀请，在每一次章节结束后
    'baoxiang',  # 在外面的地图领宝箱
    'search',
    '28',  # 选中的阶段之前
    'not_hard',
    'create',  # 组队，要放在probe前
    'probe',  # 进入界面前的
    'locked',
    'team_fight',
    'room',
    'boss_fight',
    'chapter_fight',  # 准备阶段的
    'watch',  # 观战
    'check_man',  # 检验是否需要更换狗粮
    'exchange',  # 更换狗粮
    'all',  # 组队时队员没有 exchange
    'victory',
    'fail',
    'award',
    'box',  # 这边开始是在一轮挑战过程中用到的
    'box_confirm',  # 确认式神点击盒子
]

common_prepare = [
    'baoxiang',
    'search',
    '28',  # 选中的阶段之前
    'probe',  # 进入界面前的
]
team_prepare = [
    'yes',  # 确认邀请,
    'create',  # 组队，要放在probe前
    'team_fight',
    'room'
]
chapter_fights = ['team_fight', 'boss_fight']
chapter_before_boss = [
    'chapter_fight',
    'watch',
    'check_man',
    'exchange',
    'all',
    'victory',
    'fail',
    # 'award',  # award因为award可能重入两次，所以跟box交叉了
]
chapter_between_prepare_award = [
    'watch', 'check_man', 'exchange', 'victory', 'fail', 'award'
]
box_confirm = ['box', 'box_confirm']

chapter_pics = [
    ['general', 'locked'],  # 是否锁定状态
    ['general', 'unlocked'],  # 是否锁定状态
    ['general', 'return'],
    ['chapter', '28'],
    ['chapter', 'hard'],
    ['chapter', 'not_hard'],
    ['chapter', 'probe'],
    ['general', 'room'],  # 个人空间
    ['chapter', 'boss_fight'],
    ['chapter', 'chapter_fight'],
    ['general', 'watch'],  # 观战界面
    ['chapter', 'check_man'],  # 检查是否为初始需要检查式神满级情况的界面
    ['chapter', 'box'],
    ['chapter', 'box_confirm'],
    ['chapter', 'build_team'],
    ['chapter', 'unopen'],  # 不公开
    ['chapter', 'create'],
    ['chapter', 'selected'],  # 选中框，配置unopen，选中不公开
    ['chapter', 'invite'],
    ['chapter', 'last_invite'],
    ['chapter', 'baoxiang'],
]


class ChapterCaptain(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(ChapterCaptain, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()
        self.is_captain = self.config.get('captain', True)
        self.is_captain_take_output_role = self.config.get(
            'captain_output', False)
        self.players = self.config.get('players', 1)
        self.wait_player = True if (self.is_captain
                                    and self.players > 1) else False
        self.wait_time = 0.5

        # 将图片打开成图像 ims
        self.pics = chapter_pics
        self.pics.extend(self.basic_pics)
        self.pics.extend(self.exchange_pics)
        self.pics.extend(self.team_pics)
        self.ims = screenshot.open_image_list(self.pics)

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

        # 是队员时就不用再确认是不是要进循环了
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
            if key == 'search':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
            elif key == '28':
                # 可重入2次确保可以点击成功
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
            elif key == 'probe':
                # 可重入2次确保可以点击成功
                self.display_msg('点击：{0}进入下一步'.format(key))
                return True
            last_state = key
            time.sleep(1)
        self.display_msg('未能进入到循环状态，正在退出')
        return False

    def get_fodder_status(self):
        '''
            @function: 满级匹配的结果，0未满级，1输出式神满级，2狗粮满级
            @return: [x,x,x]
        '''
        result = [0, 0, 0]  # 存储匹配的结果，0未满级，1输出式神满级，2狗粮满级

        if self.players == 1:
            # 单人时第一个位置给输出式神，取后两个位置： [190, 170, 136, 130]
            man_locs = [[375, 240, 140, 170], [610, 270, 170, 200]]
        else:
            if self.is_captain_take_output_role:
                # 队长且携带输出时，取第二排的第二个位置
                man_locs = [[443, 432, 167, 175]]
            else:
                man_locs = [[9, 267, 157, 200], [443, 432, 167, 175]]

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
        if self.players == 1:
            # 第三个位置是输出式神，可以忽略[905, 130, 130, 240]
            # 取前两个位置来替换，[970, 340]
            role_locs = [[92, 130, 184, 240], [475, 130, 205, 240]]
            final_locs = [[175, 400], [475, 360]]
        else:
            # 组队时，如果队长带输出式神
            if self.is_captain_take_output_role:
                role_locs = [[252, 158, 144, 195]]
                final_locs = [[309, 334]]
            else:
                # 取1，3位置的卡来替换
                role_locs = [[252, 158, 144, 195], [786, 158, 110, 175]]
                final_locs = [[309, 334], [843, 321]]

        return self.exchange_man_role_by_locs(role_locs, final_locs)

    def remove_list(self, src, removes):
        '''从src中删除列表removes中的元素'''
        return list(set(src) - set(removes))

    def loop(self):
        total_times = self.config.get('times', 200)
        change_loop_times = 0
        last_state = ''
        not_found_times = 0
        is_boss = False
        status = [0, 0, 0]  # 存储匹配的结果，0未满级，1输出式神满级，2狗粮满级

        global stages_loop
        change_loop = []
        while self.stop is False and change_loop_times < total_times:
            found = False
            key = ''
            im_yys = self.screenshot()
            if len(change_loop) > 0:
                check_loop = change_loop
            else:
                check_loop = stages_loop

            start = datetime.now().timestamp()

            # 此处要改成对应的loop结构体
            for key in check_loop:
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
                elif not_found_times > 33:
                    self.display_msg(
                        '超过{0}次未匹配，休眠{0}秒'.format(not_found_times))
                elif not_found_times > 3:
                    '''多次匹配不上时，说明可能是需要调整回所有循环了，需要拖动界面'''
                    if not_found_times > 10:
                        change_loop = stages_loop
                    loc_tmp = self.locate_im(self.ims['unlocked'], im_yys)
                    if loc_tmp:
                        # 正数表示界面左移（右拉），负数表示界面右移（左拉）
                        dis = 250 if not_found_times > 7 else -250
                        self.display_msg('超过{0}次未匹配，拉动距离{1}'.format(
                            not_found_times, dis))
                        self.move_loc_exact(self.x_top + self.win_width / 2,
                                            self.y_top + 150, 0.2)
                        self.dragRel_loc_exact(dis, 0, 1)
                end = datetime.now().timestamp()
                self.display_msg('本轮未匹配到截图，耗时：{0}'.format(end - start))
                time.sleep(0.5)
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            end = datetime.now().timestamp()
            self.display_msg('本轮匹配：{0}，耗时{1}'.format(key, end - start))

            self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key

            if key in ['search', '28', 'accept']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            elif key == 'yes':
                '''确认继续邀请队友时，等待3S等队伍接受邀请'''
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            elif key == 'not_hard':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                stages_loop.remove('not_hard')  # 解锁之后可以从循环中剔除了

            elif key == 'probe':
                if self.wait_player:
                    loc_tmp = self.locate_im(self.ims['build_team'], im_yys)
                    if loc_tmp:
                        self.display_msg('点击：{0}进入下一步'.format('build_team'))
                        self.click_loc_one(loc_tmp)
                else:
                    self.display_msg('点击：{0}进入下一步'.format(key))
                    self.click_loc_one(loc)
                    change_loop = stages_loop.copy()
                    change_loop = self.remove_list(change_loop, common_prepare)
                    change_loop = self.remove_list(change_loop, team_prepare)
                    change_loop = self.remove_list(change_loop, box_confirm)

            elif key == 'create':
                loc_unopen = self.locate_im(self.ims['unopen'], im_yys)
                loc_selected = self.locate_im(self.ims['selected'], im_yys)
                if loc_unopen and loc_selected:
                    if fabs(loc_selected.top - loc_unopen.top) < 30:
                        self.display_msg('已选择不公开')
                        loc_create = self.locate_im(self.ims['create'], im_yys)
                        if loc_create:
                            # 界面中会有两个创建，要创建按钮的那个
                            self.display_msg('点击：{0}进入下一步'.format('create'))
                            self.click_loc_inc(loc_create.left,
                                               loc_create.top + 292, 1)
                    else:
                        self.display_msg('点击：{0}进入下一步'.format('不公开'))
                        self.click_loc_inc(loc_unopen.left - 25,
                                           loc_unopen.top + 5, 1)
                        continue

            elif key == 'team_fight':
                # 有最近邀请界面先选中要邀请的好友
                loc_invite = self.locate_im(self.ims['last_invite'], im_yys)
                if loc_invite:
                    self.display_msg('点击：{0}进入下一步'.format('last_invite'))
                    self.click_loc_inc(loc_invite.left - 50,
                                       loc_invite.top + 20, 1)
                    time.sleep(0.5)

                # 有邀请界面时，点击邀请
                loc_invite = self.locate_im(self.ims['invite'], im_yys)
                if loc_invite:
                    self.display_msg('点击：{0}进入下一步'.format('invite'))
                    self.click_loc_one(loc_invite)
                    time.sleep(0.5)
                    continue

                # 没有邀请界面时，确认是否有队员缺席
                loc_absent = self.locate_im(self.ims['absent'], im_yys)
                if loc_absent:
                    self.display_msg('点击：{0}进入下一步'.format('absent'))
                    self.click_loc_one(loc_absent)
                    time.sleep(0.5)
                    continue

                # 上述都没有时，说明队友已经进入队伍，可以开始挑战
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                change_loop = stages_loop.copy()
                change_loop = self.remove_list(change_loop, common_prepare)
                change_loop = self.remove_list(change_loop, team_prepare)
                change_loop = self.remove_list(change_loop, box_confirm)

            elif key == 'room':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_inc(self.win_width / 2, self.win_height / 2, 1)

            elif key in ['locked']:
                stages_loop.remove(key)
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_exact(self.x_top + loc.left + 5,
                                     self.y_top + loc.top + 5, 1)  # 图片太小

            elif key in ['boss_fight', 'chapter_fight']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                is_boss = True if key == 'boss_fight' else False
                time.sleep(1.0)  # 多休息一点时间，等待挑战完成

                change_loop = self.remove_list(change_loop, common_prepare)
                change_loop = self.remove_list(change_loop, team_prepare)
                change_loop = self.remove_list(change_loop, box_confirm)
                change_loop = self.remove_list(change_loop, chapter_fights)

            elif key == 'watch':
                self.display_msg('进入到了观战界面：切换回去')
                loc_tmp = self.locate_im(self.ims['return'])
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format('return'))
                    self.click_loc_one(loc_tmp)

            elif key == 'check_man':
                status = self.get_fodder_status()
                self.display_msg('状态：{0}，狗粮状态：{1}'.format('check_man', status))
                if 2 in status:
                    # 点击进入切换狗粮界面
                    self.click_loc_exact(self.x_top + 340, self.y_top + 465, 1)
                else:
                    loc_tmp = self.locate_im(self.ims['prepare'])
                    if loc_tmp:
                        self.display_msg('无需换狗粮，点击：{0}进入下一步'.format('prepare'))
                        if self.wait_player:
                            self.display_msg('队长多等待0.5S')
                            time.sleep(self.wait_time)
                        self.click_loc_one(loc_tmp)
                        time.sleep(1.5)  # 多休息一点时间，等待挑战完成
                        change_loop = chapter_between_prepare_award

            elif key in ['exchange', 'all']:
                # 组队时队员没有 exchange
                result = self.get_exchange_fodder_status()
                self.display_msg('共更换了{}只狗粮'.format(result.count(2)))
                loc_tmp = self.locate_im(self.ims['prepare'])
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format('prepare'))
                    if self.wait_player:
                        self.display_msg('队长多等待0.5S')
                        time.sleep(self.wait_time)
                    self.click_loc_one(loc_tmp)
                    time.sleep(1.5)  # 多休息一点时间，等待挑战完成
                    change_loop = chapter_between_prepare_award

            elif key in ['victory', 'fail', 'award', 'box_confirm']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'award':
                    if is_boss:
                        change_loop_times += 1
                        change_loop = stages_loop.copy()
                        change_loop = self.remove_list(change_loop,
                                                       chapter_before_boss)
                        if self.players == 1:
                            change_loop = self.remove_list(
                                change_loop, team_prepare)
                        self.display_msg('当前进度：{0}/{1}'.format(
                            change_loop_times, total_times))
                    else:
                        change_loop = stages_loop.copy()
                        change_loop = self.remove_list(change_loop,
                                                       common_prepare)
                        change_loop = self.remove_list(change_loop,
                                                       team_prepare)
                        change_loop = self.remove_list(change_loop,
                                                       box_confirm)
                    is_boss = False
                random_dis = randint(-10, 10)
                last_x = self.x_top + 955 + random_dis
                last_y = self.y_top + 530 + random_dis
                self.click_loc_exact(last_x, last_y, 2, 0.2)  # 点击两下显示更快
                continue

            elif key in ['box', 'baoxiang']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            time.sleep(0.5)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'ChapterCaptain'

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
    chapter = ChapterCaptain()
    chapter.run()
