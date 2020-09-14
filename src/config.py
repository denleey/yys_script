#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# %% 加载基础库
import configparser
import os
import sys

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
conf_path = os.path.join(cur_dir, 'conf', 'config.ini')
#conf_path = os.path.abspath(r'F:\gitee\knowledge\Python\yys_script\src\conf\config.ini')


class Config:
    def __init__(self):
        # 打开config文件，要以utf-8的方式打开，否则中文乱码
        self.config = configparser.RawConfigParser()
        self.config.read(conf_path, encoding='utf-8')
        self.general = {}
        self.yuling = {}
        self.yuhun = {}
        self.yeyuanhuo = {}
        self.chapter = {}
        self.yys_break = {}
        self.upgrade = {}
        self.init_config()

    def read_option_str(self, section, option, default):
        try:
            return self.config.get(section, option)
        except Exception as error:
            print('获取{0},{1}失败, {2}'.format(section, option, str(error)))
            return default

    def read_option_int(self, section, option, default):
        try:
            return self.config.getint(section, option)
        except Exception as error:
            print('获取{0},{1}失败, {2}'.format(section, option, str(error)))
            return default

    def read_option_bool(self, section, option, default):
        try:
            return self.config.getboolean(section, option)
        except Exception as error:
            print('获取{0},{1}失败, {2}'.format(section, option, str(error)))
            return default

    def init_config(self):
        # sections = config.sections()  # [str]
        # general_options = config.options('general')   # [str]
        # config.get('general', 'title')
        self.general['title'] = self.read_option_str('general', 'title',
                                                     'x笑cry-辅助工具')
        self.general['version'] = self.read_option_str('general', 'version',
                                                       'v2.2.2')
        self.general['attention'] = self.read_option_str(
            'general', 'attention', '').replace(r'\n', '\n')
        self.general['gitpath'] = self.read_option_str(
            'general', 'gitpath', '').replace(r'\n', '\n')

        self.yuhun['times'] = self.read_option_int('yuhun', 'times', 200)
        self.yuhun['players'] = self.read_option_int('yuhun', 'players', 2)
        self.yuhun['may_fail'] = self.read_option_bool('yuhun', 'may_fail',
                                                       True)
        self.yuhun['captain'] = self.read_option_bool('yuhun', 'captain', True)
        self.yuhun['attention'] = self.read_option_str('yuhun', 'attention',
                                                       '').replace(
                                                           r'\n', '\n')

        self.yuling['times'] = self.read_option_int('yuling', 'times', 200)
        self.yuling['type'] = self.read_option_str('yuling', 'type', 'dragon')
        self.yuling['layer'] = self.read_option_int('yuling', 'layer', 3)
        self.yuling['attention'] = self.read_option_str(
            'yuling', 'attention', '').replace(r'\n', '\n')

        self.yeyuanhuo['times'] = self.read_option_int('yeyuanhuo', 'times',
                                                       200)
        self.yeyuanhuo['layer'] = self.read_option_int('yeyuanhuo', 'layer', 3)
        self.yeyuanhuo['attention'] = self.read_option_str(
            'yeyuanhuo', 'attention', '').replace(r'\n', '\n')

        self.yys_break['attention'] = self.read_option_str(
            'yys_break', 'attention', '').replace(r'\n', '\n')

        self.chapter['players'] = self.read_option_int('chapter', 'players', 1)
        self.chapter['times'] = self.read_option_int('chapter', 'times', 200)
        self.chapter['attention'] = self.read_option_str(
            'chapter', 'attention', '').replace(r'\n', '\n')

        self.upgrade['times'] = self.read_option_int('upgrade', 'times', 200)
        self.upgrade['attention'] = self.read_option_str(
            'upgrade', 'attention', '').replace(r'\n', '\n')


config = Config()
general = config.general
yuhun = config.yuhun
yuling = config.yuling
yeyuanhuo = config.yeyuanhuo
yys_break = config.yys_break
chapter = config.chapter
upgrade = config.upgrade

if __name__ == '__main__':
    print(general.keys())
    for key in general:
        print(key, general[key])

    print(yuhun.keys())
    for key in yuhun:
        print(key, yuhun[key])

    print(yuling.keys())
    for key in yuling:
        print(key, yuling[key])
