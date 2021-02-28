# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# 「ル」の字
TL_ru = (914, 150)
BR_ru = (944, 216)
# ルール名
TL_rule = ( 840, 290)
BR_rule = (1080, 490)

# 一致率の閾値 threshold
thd_val = 0.95

# ルール一覧
rule_list = ['turf', 'zones', 'tower', 'rain', 'clam']

# 「ル」画像
bin_ru = cv2.imread('.\\pbm\\rule.pbm', -1)


def judgeRule(frame):
    ''' ルール表示フレームの判定 '''
    # 「ル」一致率算出
    val = iip.getMatchValue(bin_ru, frame, TL_ru, BR_ru)
    # 閾値以上ならばルール表示
    judge = True if val > thd_val else False

    return judge


def getRule(frame):
    ''' ルール取得 '''
    # ルール画像読み込み
    image_list = []
    for rule_name in rule_list:
        bin_rule = cv2.imread('.\\pbm\\rule_' + rule_name + '.pbm', -1)
        image_list.append(bin_rule)

    # 最も一致するルールを探す
    index = iip.getMostMatchImage(frame, TL_rule, BR_rule, image_list)
    rule = rule_list[index]

    return rule