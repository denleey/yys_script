# -*- coding: utf-8 -*-

import os
import sys
import logging
from PIL import Image

screenshot_dir = os.path.split(os.path.abspath(
    sys.argv[0]))[0] + os.path.sep + 'screenshot'


def open_image_list(pics):
    '''按目录层级打开相应的所有图片，并使用每个name作为key
        [
            [dir1, dir2, name1],
            [dir1, dir2, name2]
        ]
    '''
    ims = {}
    for onepath in pics:
        base_dir = screenshot_dir
        if onepath:
            key = onepath[-1]
            for relative in onepath:
                base_dir = os.path.join(base_dir, relative)
            filepatch = base_dir + '.jpg'

            try:
                im = Image.open(filepatch)
                # logging.debug('打开图片：{0}'.format(filepatch))
                # im.show()
                ims[key] = im
                # ims[key].show()
            except Exception as error:
                logging.error('打开图片失败，{0}, msg:{1}'.format(filepatch, error))
    return ims


if __name__ == '__main__':
    yuling_pics = [
        ['general', 'search'],  # 搜索
        ['general', 'fight'],  # P0挑战
        ['general', 'prepare'],  # P1准备
        ['general', 'victory'],  # 结算胜利
        ['general', 'fail'],  # 结算失败
        ['general', 'award'],  # 结算达摩
        ['yuling', 'layer3'],  # 选择第几层
        ['yuling', 'dragon'],  # 神龙
        ['yuling', 'fox'],  # 狐狸
        ['yuling', 'leopard'],  # 狐狸
        ['yuling', 'phenix'],  # 狐狸
    ]
    ims = open_image_list(yuling_pics)
