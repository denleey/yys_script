# /d/env/Python37/python
# -*- coding:utf-8 -*-

# %%
# import os
# import sys
# import random
from PIL import Image, ImageGrab
# import cv2
# import win32gui win32con win32api
# import numpy as np

# %% 初始化日志，方便打印
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format=
    '%(asctime)s: [%(filename)s:line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d-%H:%M:%S',
    filename=None,
    filemode='match_width')

# %% 获取到阴阳师窗体信息
import win32gui

win_name = '阴阳师-网易游戏'
yys_handler = win32gui.FindWindow(0, win_name)  # 获取窗口句柄
if yys_handler == 0:
    logging.error('获取不到阴阳师窗体' + str(yys_handler))
else:
    logging.info('获取到阴阳师窗体' + str(yys_handler))

# %% 获取到窗体的位置
x_top, y_top, x_bottom, y_bottom = win32gui.GetWindowRect(yys_handler)
win_width = x_bottom - x_top
win_height = y_bottom - y_top
logging.info('位置信息：({0},{1}), ({2},{3})'.format(x_top, y_top, x_bottom,
                                                y_bottom))
logging.info('窗体大小：width={0}, height{1})'.format(win_width, win_height))

# %% 重新设置大小
import win32con
# 没有管理员权限的话是无法移动的，移动时限制了比例，以height=640为准(1083, 640)
# x_top = y_top = 0
win_width = 1152
win_height = 679
x_bottom = x_top + win_width
y_bottom = y_top + win_height
try:
    win32gui.SetWindowPos(yys_handler, win32con.HWND_NOTOPMOST, x_top, y_top,
                          win_width, win_height, win32con.SWP_SHOWWINDOW)
except Exception as error:
    logging.error('请确认你拥有管理员权限，否则无法重新设置大小，msg:{0}'.format(error))

# %% 先截个全图看看是不是正确，可能是我哪里参数有问题，CV图的显示有点问题。
# 所以还是直接用 PIL 的库显示
# logging.debug('截图信息：({0},{1} -> ({2},{3}))'.format(x_top, y_top, x_bottom, y_bottom))
# img_intact = ImageGrab.grab((x_top, y_top, x_bottom, y_bottom))
# # img_intact.show()
# img_intact_cv = pil2cv(img_intact)

# %% 使用 pyautogui 快速截图整个游戏界面
import pyautogui
im_yys = pyautogui.screenshot(region=(x_top, y_top, win_width, win_height))
logging.debug('截图信息：{0},{1}'.format((x_top, y_top, win_width, win_height),
                                    im_yys.mode))
# im.show()

import os, sys, time
cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
cur_dir = os.path.dirname(cur_dir) + os.path.sep + 'src'
filepatch = os.path.join(cur_dir, 'screenshot', 'chapter', 'last_invite.png')
# filepatch = os.path.join(cur_dir, 'screenshot', 'general', 'fight.png')
# filepatch = os.path.join(cur_dir, 'screenshot', 'role', 'marked.png')
# filepatch = os.path.join(cur_dir, 'screenshot', 'break', 'over.png')
# filepatch = os.path.join(cur_dir, 'screenshot', 'yuhun', 'p1.png')
# filepatch = os.path.join(cur_dir, 'screenshot', 'yuhun', 'absent.png')
print(filepatch)
im = Image.open(filepatch)

# im_special = pyautogui.screenshot(region=(x_top + 365, y_top + 568, 30, 30))
# im_yys = im_special
# im_special.show()

for i in range(10):
    im_yys = pyautogui.screenshot(region=(x_top, y_top, win_width, win_height))
    if i == 0:
        # im_yys.show()
        im.show()
    loc = pyautogui.locate(im, im_yys, confidence=0.8)
    if loc is not None:
        print(x_top + loc.left, y_top + loc.top)
    else:
        print('not found')
    time.sleep(1.5)

# 点击并拖动
# pyautogui.moveTo(x_top + loc.left - 20, y_top + loc.top + 50, 1)
# print('移动位置', x_top + loc.left - 20, y_top + loc.top + 50)
# time.sleep(1)
# # pyautogui.click(x_top + loc.left + 5, y_top + loc.top + 5, 1, 0, button='left')
# x_offset = ((x_top + 395) - (x_top + loc.left - 20)) * 1.0
# y_offset = ((y_top + 290) - (y_top + loc.top + 50)) * 1.0
# print('拖动位置', x_offset, y_offset)
# pyautogui.dragRel(x_offset, y_offset, duration=1.5)
