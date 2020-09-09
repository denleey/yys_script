# /usr/bin/python
# -*- coding: utf-8 -*-

import os


def do_shell_command(command):
    res = os.popen(command).readlines()
    return res


if __name__ == '__main__':
    print('正在安装依赖库')
    pip_list = [
        'pyautogui', 'pywin32', 'PyQt5', 'pyqt5-tools', 'configparser'
    ]

    # 先更新pip的版本
    res = do_shell_command('python -m pip install --upgrade pip')
    for each_lib in pip_list:
        res = do_shell_command('pip install {}'.format(each_lib))
        print('安装：{0}，状态：{1}'.format(each_lib, res))
