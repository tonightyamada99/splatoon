# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# ステージ名の座標
TL_stage = (1500,  972)
BR_stage = (1890, 1053)

# RGBの閾値[min, max](0~255, 0~255, 0~255)
thd_rgb = {'stg':[(224, 224, 224), (255, 255, 255)]}


def getStage(frame):
    ''' ステージ取得 '''
    # ステージ画像読み込み
    image_list = []
    for i in range(23):
        bin_rule = cv2.imread('.\\pbm\\stage_name_' + str(i) + '.pbm', -1)
        image_list.append(bin_rule)

    # 最も一致するステージ画像を探す
    # インデックスがそのままステージ番号
    stage_num = iip.getMostMatchImage(frame, TL_stage, BR_stage, image_list,
                                      threshold=thd_rgb['stg'])

    return stage_num