# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip

'''''''''''''''''''''''''''''''''''''''''''''''
カウント表示がガチヤグラと同様のため
確保状況・位置・カウント数字の認識は
towerの名前のものを使用します
異なる点
ホコ  ：最初はカウント表示なし（最高99）
ヤグラ：最初からカウント表示あり（最高100）
'''''''''''''''''''''''''''''''''''''''''''''''

# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# 位置表示メーター
TL_mtr = ( 490, 140)
BR_mtr = (1430, 168)
# 位置表示の左右端
L_end =  514
R_end = 1406
# カウントのこり
T_rmn = 202
B_rmn = 218
L_rmn = [ 930, 480]
R_rmn = [1440, 990]
# カウント数字 ※左右は「のこり」の位置から決定
T_cnt = 216
B_cnt = 256

# 「のこり」の一致率
thd_rmn = 0.75
# カウント表示の幅
width_count = 64

# 色閾値 threshold
# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'wht':[(128, 128, 128), (255, 255, 255)]}

# 位置アイコン画像
image_icn = []
for name in ['neutral', 'alfa', 'bravo']:
    bin_icn = cv2.imread('.\\pbm\\tower_meter_' + name + '.pbm', -1)
    image_icn.append(bin_icn)

# 「のこり」画像
image_rmn = []
for ab in ['alfa', 'bravo']:
    bin_rmn = cv2.imread('.\\pbm\\tower_remaining_' + ab + '.pbm', -1)
    image_rmn.append(bin_rmn)

# 数字画像
image_act = []  # アルファ
image_bct = []  # ブラボー
for num in range(10):
    bin_num = cv2.imread('.\\pbm\\tower_alfa_' + str(num) + '.pbm', -1)
    image_act.append(bin_num)
    bin_num = cv2.imread('.\\pbm\\tower_bravo_' + str(num) + '.pbm', -1)
    image_bct.append(bin_num)


def listtop():
    ''' 記録リストの先頭行を返す '''
    list_top = ['control', 'location', 'count_alfa', 'count_bravo']

    return list_top


def forFrame(frame):
    ''' フレームに対しての一連の処理を行う '''
    # 確保状況
    control, location = getControl(frame)
    # カウント
    count_list = getCount(frame)
    # 出力リスト
    out_list = [control, location] + count_list

    return out_list


def getControl(frame):
    ''' ガチホコの確保状況と位置を取得する '''
    # ホコの確保状況 in control -> 0:neutral 1:alfa 2:bravo
    control = 0

    # 位置表示部分の切り取り
    l, t = TL_mtr
    r, b = BR_mtr
    img_trm = frame[t:b, l:r]
    # 白で二値化
    bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])

    # それぞれの確保状況のアイコンで一致率を比較する
    # アイコンの位置も取得する
    val_meter = 0
    loc_meter = 0
    for i  in range(3):
        # アイコン画像
        bin_icn = image_icn[i]
        # 一致率と位置を算出
        jug = cv2.matchTemplate(bin_trm, bin_icn, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)

        # 一致率を比較
        if maxVal > val_meter:
            val_meter = maxVal

            # 記録する座標はアイコンの中心
            width = bin_icn.shape[1]
            loc_meter = round(TL_mtr[0] + maxLoc[0] + width / 2)
            # 確保状況 == インデックス
            control = i

    # 位置は-1~1の範囲で出力する
    # -1:ブラボーのゴール（左端） 1:アルファのゴール（右端）
    center = (L_end + R_end) / 2
    location = (loc_meter - center) / (R_end - center)

    return control, location


def getCount(frame):
    ''' カウントを取得する '''
    # 記録リスト
    count_list = ['nodata', 'nodata']

    # アルファとブラボー
    for i in range(2):
        # 「のこり」部分の切り取り
        t = T_rmn
        b = B_rmn
        l = L_rmn[i]
        r = R_rmn[i]
        img_trm = frame[t:b, l:r]
        # 白で二値化
        bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])
        # 「のこり」画像
        bin_rmn = image_rmn[i]
        # 一致率と位置を算出
        jug = cv2.matchTemplate(bin_trm, bin_rmn, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)

        # 表示が重なってカウントが見えない場合があるので閾値を設ける
        if maxVal > thd_rmn:
             # 「のこり」の位置から数字の左右位置を算出
            width_rmn = bin_rmn.shape[1]
            center = L_rmn[i] + maxLoc[0] + width_rmn / 2
            left  = round(center - width_count / 2)
            right = round(center + width_count / 2)
            # カウント座標
            TL = (left,  T_cnt)
            BR = (right, B_cnt)
            # 数字画像
            image_num = image_act if i == 0 else image_bct
            # カウント数字取得
            count = iip.getNumber(frame, TL, BR, image_num)
            # リストに記録
            count_list[i] = count

    return count_list