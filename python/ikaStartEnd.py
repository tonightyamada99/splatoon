# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# 時計
TL_tim = ( 912, 54)
BR_tim = (1008, 99)
# FINISH!
TL_fin = (380, 630)
BR_fin = (690, 720)

# 一致率の閾値 threshold
thd_val = 0.95

# 比較画像
# 試合開始ナワバリ
bin_259 = cv2.imread('.\\pbm\\time_259.pbm', -1)
# 試合開始ガチルール
bin_459 = cv2.imread('.\\pbm\\time_459.pbm', -1)
# 試合終了
bin_fin = cv2.imread('.\\pbm\\time_fin.pbm', -1)


def judgeStartTurf(frame):
    ''' ナワバリ試合開始の判定 '''
    # 「2:59」との一致率算出
    val = iip.getMatchValue(bin_259, frame, TL_tim, BR_tim)
    # 閾値以上ならば試合開始
    judge = True if val > thd_val else False

    return judge


def judgeStartGachi(frame):
    ''' ガチルール試合開始の判定 '''
    # 「4:59」との一致率算出
    val = iip.getMatchValue(bin_459, frame, TL_tim, BR_tim)
    # 閾値以上ならば試合開始
    judge = True if val > thd_val else False

    return judge


def judgeEnd(frame):
    ''' 試合終了の判定 '''
    # 「FINISH」との一致率算出 ※基準色は黒
    val = iip.getMatchValue(bin_fin, frame, TL_fin, BR_fin, 'blk')
    # 閾値以上ならば試合終了
    judge = True if val > thd_val else False

    return judge