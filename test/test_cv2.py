# -*- coding: utf-8 -*-

'''
1. pillow <-> opencv


pillow和opencv互转： <https://qiita.com/derodero24/items/f22c22b22451609908ee>
'''

from PIL import ImageGrab, Image
import cv2
import os, sys
import numpy as np
import win32gui

def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

def get_window_handler(win_name: str):
    '''获取阴阳师窗口的句柄信息
    '''
    handle = win32gui.FindWindow(0, win_name)  # 获取窗口句柄
    if handle == 0:
        return None
    else:
        return win32gui.GetWindowRect(handle)


def mathc_img(Target, value = 0.9):
    try:
        img = cv2.imread(r'C:\Users\caiyx\Desktop\all.png')

        handler = get_window_handler('阴阳师-网易游戏')
        img_intact = ImageGrab.grab((handler[0], handler[1], handler[2], handler[3]))
        img = pil2cv(img_intact)

        template = cv2.imread(r'C:\Users\caiyx\Desktop\yuling_fight.png')
        # template = pil2cv(Image.open(r'C:\Users\caiyx\Desktop\yuling_fight.png'))
        # dirname = os.path.split(os.path.abspath(sys.argv[0]))[0]
        # filepath = os.path.join(dirname, 'screenshot', 'yuling_fight.png')
        # template = cv2.imread(filepath, 0)

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(min_val, max_val, min_loc, max_loc)

        left_top = max_loc  # 左上角
        h, w = template.shape[:2]  # rows->h, cols->w
        right_bottom = (left_top[0] + w, left_top[1] + h)  # 右下角
        cv2.rectangle(img, left_top, right_bottom, 255, 2)  # 画出矩形位置
    except Exception as error:
        raise Exception('未匹配到图片' + str(error))

mathc_img(r'C:\Users\xxx\Desktop\yuling_fight.png')
