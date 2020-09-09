# -*- coding: utf-8 -*-

# %%
import win32gui
import win32con
import logging

# %% 获取阴阳师窗口的句柄信息
logging.basicConfig(level=logging.DEBUG)
win_name = '阴阳师-网易游戏'
win_handler = win32gui.FindWindow(0, win_name)  # 获取窗口句柄
if win_handler == 0:
    logging.error('请确认游戏是否已经开启')
    exit()

x_top, y_top, x_bottom, y_bottom = \
    win32gui.GetWindowRect(win_handler)
win_width = x_bottom - x_top
win_height = y_bottom - y_top
logging.debug('捕获到程序：{0},({1},{2}),{3},{4}'.format(win_name, x_top, y_top,
                                                   win_width, win_height))

# %% 调整窗体大小，无法调整时会抛异常
new_width = 1152
new_height = 679
try:
    win32gui.SetWindowPos(win_handler, win32con.HWND_NOTOPMOST, x_top, y_top,
                          new_width, new_height, win32con.SWP_SHOWWINDOW)
except Exception as error:
    raise ('请确认你拥有管理员权限，否则无法重新设置大小，msg:{0}'.format(error))
