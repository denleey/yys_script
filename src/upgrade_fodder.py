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
    1. 返回 -> 式神录
    2. 类型 -> 育成
            1. 首次进入时
                排列类型 -> 宽松排列（大图标）
                排列类型 -> 星级排列
            2. 首次标记星级时
                切换到2星，3星
            3. 遍历12个格式
                存在满级时
                    点击风格中间 -> 点击育成
                首次切换时，切换为稀有度，交选中两张N卡，3星时根据配置决定没有N卡时是否选择白蛋（不建议选）
                点击前两格的中间选中 -> 确认(注意是确认，不是确定) -> 点击确定
            4. 重复3
'''

stages_prepare = [
    'main_return',  # 庭院里面的返回
    'roles_data',  # 式神录
    'foster',  # 育成
]
stages_loop = ['foster', 'confirm', 'yes']  # 不适合用原来的框架

upgrade_pics = [
    ['general', 'main_return'],
    ['general', 'confirm'],  # 确认，不是确定
    ['general', 'yes'],  # 确认，不是确定
    ['upgrade', 'roles_data'],  # 式神录
    ['upgrade', 'type'],  # 类型排列选择 -> 宽松排列，星级排序
    ['upgrade', 'relax'],  # 宽松排列
    ['upgrade', 'stars'],  # 按星级排序
    ['upgrade', 'man'],  # 满，小的满
    ['upgrade', 'fodder_select'],  # 选择要使用的狗粮类型 -> 按稀有度
    ['upgrade', 'fodder_relax'],  # 选择宽松排序
    ['upgrade', 'rarity'],  # 按稀有度排序
    ['upgrade', 'not_enough'],  # 按稀有度排序
    ['upgrade', 'fodder'],  # 素材
    ['upgrade', 'ncard'],  # N卡
    ['upgrade', 'foster'],  # 育成
]


class Upgrade(AutoGui):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, parent=None, config={}, win_name='阴阳师-网易游戏'):
        super(Upgrade, self).__init__(parent)
        self.parent = parent
        self.win_name = win_name
        self.config = config
        self.select_stars = self.config.get('select_stars', 3)
        self.fodder_type = self.config.get('fodder_type', 'ncard')
        self.init_attribute()

        # 将图片打开成图像 ims
        self.pics = upgrade_pics
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
            if key in ['main_return', 'roles_data']:
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
            elif key == 'foster':
                self.display_msg('点击：{0}进入下一步'.format(key))
                return True
            time.sleep(1)
        self.display_msg('未能进入到循环状态，正在退出')
        return False

    def loop(self):
        total_times = self.config.get('times', 200)
        cur_loop_times = 0
        last_state = ''
        not_found_times = 0

        already_arrange_relax = False  # 宽松排列
        already_arrange_stars = False  # 按星级排列
        already_select_stars = False  # 选择升级的狗粮星级
        already_arrange_fodder = False  # 用来升级的狗粮排列类型
        already_change_rarity = False  # 用来设置狗粮的稀有度，即用N卡还是白蛋来喂

        is_in_foster = False

        mid_inc_x = 40
        mid_inc_y = 70
        roles_boxes = [[65, 190, 85, 145], [160, 190, 85, 145],
                       [255, 190, 85, 145], [350, 190, 85, 145],
                       [65, 340, 85, 145], [160, 340, 85, 145],
                       [255, 340, 85, 145], [350, 340, 85, 145],
                       [65, 485, 85, 145], [160, 485, 85, 145],
                       [255, 485, 85, 145], [350, 485, 85, 145]]

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
                    self.display_msg('未匹配到状态，休眠{0}秒'.format(10))
                    time.sleep(10)
                else:
                    time.sleep(1.5)  # 常规情况下，休眠1.5秒
                continue
            else:
                not_found_times = 0  # 重新将失败记录改为0

            self.display_msg('状态切换：{0} -> {1}'.format(last_state, key))
            last_state = key

            if key == 'foster':
                '''只有一个育成入口'''
                if already_arrange_relax is False:
                    '''选择宽松排列'''
                    loc_type = self.locate_im(self.ims['type'])
                    if loc_type:
                        self.click_loc_one(loc_type)
                        time.sleep(0.5)
                        loc_relax = self.locate_im(self.ims['relax'])
                        if loc_relax:
                            self.display_msg('标记宽松排列')
                            already_arrange_relax = True
                            self.click_loc_one(loc_relax)
                    time.sleep(0.5)
                    continue

                if already_arrange_stars is False:
                    '''选择按星级排列'''
                    loc_stars = self.locate_im(self.ims['stars'])
                    if loc_stars:
                        self.display_msg('标记按星级排列')
                        already_arrange_stars = True
                        self.click_loc_one(loc_stars)
                        time.sleep(0.5)
                        continue

                    loc_type = self.locate_im(self.ims['type'])
                    if loc_type:
                        self.click_loc_one(loc_type)
                        time.sleep(0.5)
                        loc_stars = self.locate_im(self.ims['stars'])
                        if loc_stars:
                            self.display_msg('标记按星级排列')
                            already_arrange_stars = True
                            self.click_loc_one(loc_stars)
                    time.sleep(0.5)
                    continue

                if already_select_stars is False:
                    '''选择要升级的狗粮星级'''
                    inc_y = 162
                    if self.select_stars == 3:
                        inc_x = 330
                    else:
                        inc_x = 405
                    already_select_stars = True
                    self.display_msg('选择要升级的狗粮星级')
                    self.click_loc_inc(inc_x, inc_y, 1)
                    time.sleep(0.5)
                    continue

                if is_in_foster is False:
                    '''选定要升级哪一只狗粮，并点击育成'''
                    for i in range(len(roles_boxes)):
                        loc_tmp = self.locate_im_inc(self.ims['man'],
                                                     roles_boxes[i][0],
                                                     roles_boxes[i][1],
                                                     roles_boxes[i][2],
                                                     roles_boxes[i][3])
                        if loc_tmp:
                            x_mid = roles_boxes[i][0] + mid_inc_x
                            y_mid = roles_boxes[i][1] + mid_inc_y
                            self.display_msg('选择狗粮{0}, ({1}，{2})'.format(
                                i, x_mid, y_mid))
                            self.click_loc_inc(x_mid, y_mid, 1)
                            time.sleep(0.5)
                            break

                    if i == len(roles_boxes):
                        self.display_msg('已经没有满级狗粮可以拿来升级，退出')
                        self.stop = True

                    loc_tmp = self.locate_im(self.ims['foster'])
                    if loc_tmp:
                        self.display_msg('已经选中要升级的狗粮，点击育成')
                        self.click_loc_one(loc_tmp)

            elif key == 'confirm':
                '''选择要作为狗粮的N卡或者白蛋'''
                if already_change_rarity is False:
                    already_change_rarity = True
                    '''如果已经是按稀有度排序，就不再重新选择了'''
                    if self.locate_im(self.ims['ncard']) is False:
                        loc_tmp = self.locate_im(self.ims['fodder_select'])
                        if loc_tmp:
                            self.click_loc_inc(loc_tmp.left + 10,
                                               loc_tmp.top + 5, 1)
                            time.sleep(0.5)
                        loc_tmp = self.locate_im(self.ims['rarity'])
                        if loc_tmp:
                            self.display_msg('按稀有度排序作为狗粮的式神')
                            self.click_loc_one(loc_tmp)
                            time.sleep(0.5)

                loc_tmp = self.locate_im(self.ims[self.fodder_type])
                if loc_tmp:
                    self.display_msg('选择{0}作为狗粮'.format(self.fodder_type))
                    self.click_loc_one(loc_tmp)
                    time.sleep(0.5)

                if already_arrange_fodder is False:
                    already_arrange_fodder = True
                    loc_tmp = self.locate_im(self.ims['fodder_relax'])
                    if loc_tmp:
                        self.display_msg('宽松排列作为狗粮的式神')
                        self.click_loc_one(loc_tmp)
                        time.sleep(0.5)

                for i in range(self.select_stars):
                    x_mid = roles_boxes[i][0] + mid_inc_x
                    y_mid = roles_boxes[i][1] + mid_inc_y
                    self.display_msg('选择狗粮{0}, ({1}，{2})'.format(
                        i, x_mid, y_mid))
                    self.click_loc_inc(x_mid, y_mid, 1)
                    time.sleep(0.5)
                '''点击确认升级狗粮'''
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)
                is_in_foster = False  # 将正在升级的标记清空掉
                time.sleep(0.5)
                '''狗粮不足时，自动退出升级'''
                loc_tmp = self.locate_im(self.ims['not_enough'])
                if loc_tmp:
                    self.display_msg('狗粮不足，正在退出')
                    self.stop = True
                time.sleep(1)  # 升级一只后动画比较长，等待2秒

            elif key == 'yes':
                self.display_msg('点击：{0}进入下一步'.format(key))
                self.click_loc_one(loc)

            time.sleep(1)
        self.display_msg('执行完成：正在退出')
        return False

    def run(self):
        self.auto_type = 'Upgrade'

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
    upgrade = Upgrade()
    upgrade.run()
