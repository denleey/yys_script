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
队长和队员分开，队员

队员执行步骤：
    2. 检查狗粮满的界面（准备，满, check_man）
        -> 换狗粮（满，素材，交换，全部，准备）
        -> 成功/失败 -> 达摩领取奖励
        -> 小纸人（盒子） -> 奖励确认
注意事项：
    可能点击到观战，做了容错
'''

# 注释掉的部分是其他阶段也会进入到的界面
stages_loop = [
    'accept',  # 接受邀请
    'baoxiang',
    'locked',
    'unlocked',
    'boss_fight',
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


class Chapter(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(Chapter, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.init_attribute()
        self.is_captain = False
        self.is_captain_take_output_role = self.config.get(
            'captain_output', False)
        self.players = 2

        # 将图片打开成图像 ims
        self.pics = chapter_pics
        self.pics.extend(self.basic_pics)
        self.pics.extend(self.exchange_pics)
        self.pics.extend(self.team_pics)
        self.ims = screenshot.open_image_list(self.pics)
        self.total_times = self.config.get('times', 200)

    def already_in_loop(self):
        for key in stages_loop:
            if self.locate_im(self.ims[key]):
                self.display_msg('当前状态：{0}，可进入loop'.format(key))
                return True
        return False

    def remove_list_from_src(self, src_list, remove_list):
        '''从列表中删除一组指定列表'''
        return list(set(src_list) - set(remove_list))

    def goto_loop(self):
        '''队员时直接认为可以进行循环'''
        return True

    def get_fodder_status(self):
        '''
            @function: 满级匹配的结果，0未满级，1输出式神满级，2狗粮满级
            @return: [x,x,x]
        '''
        result = [0, 0, 0]  # 存储匹配的结果，0未满级，1输出式神满级，2狗粮满级
        '''如果队长带输出式神，可以上三个狗粮，不然只能带两个狗粮'''
        if self.is_captain_take_output_role:
            man_locs = [[190, 170, 136, 130], [375, 240, 140, 170],
                        [610, 270, 170, 200]]
        else:
            man_locs = [[375, 240, 140, 170], [610, 270, 170, 200]]

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
        '''如果队长带输出式神，可以上三个狗粮，不然只能带两个狗粮'''
        if self.is_captain_take_output_role:
            role_locs = [[92, 130, 184, 240], [475, 130, 205, 240],
                         [905, 130, 130, 240]]
            final_locs = [[175, 400], [475, 360], [970, 340]]
        else:
            role_locs = [[92, 130, 184, 240], [475, 130, 205, 240]]
            final_locs = [[175, 400], [475, 360]]

        return self.exchange_man_role_by_locs(role_locs, final_locs)

    def loop(self):
        cur_loop_times = 0
        last_state = ''
        not_found_times = 0
        is_boss = False
        status = [0, 0, 0]  # 存储匹配的结果，0未满级，1输出式神满级，2狗粮满级

        global stages_loop
        check_loop = stages_loop
        while self.stop is False and cur_loop_times < self.total_times:
            found = False
            key = ''
            im_yys = self.screenshot()
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
                    # 多次匹配不上时，说明可能是需要调整回所有循环了
                    self.display_msg('超过{0}次未匹配'.format(not_found_times))

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

            if key in ['search', '28', 'not_hard', 'yes', 'accept']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            elif key in ['locked', 'unlocked']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'locked':
                    self.click_loc_exact(self.x_top + loc.left + 5,
                                         self.y_top + loc.top + 5, 1)  # 图片太小
                stages_loop.remove('locked')
                stages_loop.remove('unlocked')

            elif key in ['boss_fight', 'chapter_fight']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                is_boss = True if key == 'boss_fight' else False
                time.sleep(1.0)  # 多休息一点时间，等待挑战完成

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
                        self.click_loc_one(loc_tmp)
                        time.sleep(2)  # 多休息一点时间，等待挑战完成

            elif key in ['exchange', 'all']:
                # 组队时队员没有 exchange
                result = self.get_exchange_fodder_status()
                self.display_msg('共更换了{}只狗粮'.format(result.count(2)))
                loc_tmp = self.locate_im(self.ims['prepare'])
                if loc_tmp:
                    self.display_msg('点击：{0}进入下一步'.format('prepare'))
                    self.click_loc_one(loc_tmp)
                    time.sleep(2)  # 多休息一点时间，等待挑战完成

            elif key in ['victory', 'fail', 'award', 'box_confirm']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                if key == 'victory' and is_boss:
                    cur_loop_times += 1
                    self.display_msg('当前进度：{0}/{1}'.format(
                        cur_loop_times, self.total_times))
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
        self.auto_type = 'Chapter'

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
    chapter = Chapter()
    chapter.run()
