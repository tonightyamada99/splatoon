# -*- coding: utf-8 -*-

import cv2
import numpy as np
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD

# イカランプのサイズ名
size_list = ['SS', 'SM', 'MM', 'ML', 'LL']
# イカランプ sub:主観 obj:俯瞰
# 上
T_lamp = {'subSS':33, 'objSS':50,
          'subSM':30, 'objSM':47,
          'subMM':28, 'objMM':45,
          'subML':26, 'objML':44,
          'subLL':23, 'objLL':42}
# 下
B_lamp = {'subSS':108, 'objSS':90,
          'subSM':110, 'objSM':92,
          'subMM':113, 'objMM':94,
          'subML':115, 'objML':95,
          'subLL':117, 'objLL':96}
# 左
L_lamp = {'SS':[572, 648, 723, 799, 1051, 1127, 1202, 1278],
          'SM':[554, 635, 716, 797, 1049, 1130, 1211, 1292],
          'MM':[536, 623, 709, 795, 1047, 1133, 1219, 1306],
          'ML':[518, 610, 701, 793, 1045, 1137, 1228, 1320],
          'LL':[500, 597, 694, 791, 1043, 1140, 1237, 1334]}
# 右
R_lamp = {'SS':[642, 718, 793, 869, 1121, 1197, 1272, 1348],
          'SM':[628, 709, 790, 871, 1123, 1204, 1285, 1366],
          'MM':[614, 701, 787, 873, 1125, 1211, 1297, 1384],
          'ML':[600, 692, 783, 875, 1127, 1219, 1310, 1402],
          'LL':[586, 683, 780, 877, 1129, 1226, 1323, 1420]}
# 中央
C_lamp = {'SS':[607, 683, 758, 834, 1086, 1162, 1237, 1313],
          'SM':[591, 672, 753, 834, 1086, 1167, 1248, 1329],
          'MM':[575, 662, 748, 834, 1086, 1172, 1258, 1345],
          'ML':[559, 651, 742, 834, 1086, 1178, 1269, 1361],
          'LL':[543, 640, 737, 834, 1086, 1183, 1280, 1377]}
# 幅（半分）
W_lamp = {'SS':35, 'SM':37, 'MM':39, 'ML':41, 'LL':43}

# マップでのプレイヤー表示位置
# 味方
TL_map = [(125, 490), ( 830,  40), (1535, 490)]
BR_map = [(465, 590), (1170, 140), (1875, 590)]
# 相手（左右位置は共通）
TL_map += [(1634, t) for t in [ 52, 118, 183, 249]]
BR_map += [(1842, b) for b in [112, 178, 243, 309]]

# ブラボーチームBボタン
# Aボタンはカウント表示が被るのでBボタンを基準とする
TL_button = (1126,  95)
BR_button = (1173, 134)
# Bボタンのサイズ SS~LL
size_button = [25, 27, 28.5, 30.5, 32]
# 面積閾値
thd_button = 300   # @FHD(1920, 1080)

# 一致率
thd_val = 0.9

# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), (128, 128, 128)],
           'gry':[( 96,  96,  96), (160, 160, 160)],
           'wht':[(128, 128, 128), (255, 255, 255)]}

# HSV[min, max](0~179, 0~255, 0~255)
thd_hsv = {'blk':[(  0,   0,   0), (179,  64, 128)],    # 黒
           'wht':[(  0,   0, 128), (179,  64, 255)],    # 白
           'spw':[(  0,  16, 128), (179, 128, 255)],    # スペシャル状態
           'yel':[( 20, 128, 128), ( 30, 255, 255)],
           'blu':[(125, 128, 128), (135, 255, 255)]}

# チームカラー候補
color_catalog = ['yel', 'blu']

# マップ画面の状態画像
bin_crs = []    # バツ印
bin_spw = []    # スペシャル状態
for team in ['gg', 'bg']:   # 味方:good guys  相手:bad guys
    bin_tmp = cv2.imread('.\\pbm\\map_' + team +'_cross.pbm', -1)
    bin_crs.append(bin_tmp)
    bin_tmp = cv2.imread('.\\pbm\\map_' + team +'_spw.pbm', -1)
    bin_spw.append(bin_tmp)

# 各サイズのランプ画像
ika_list = []   # イカ
oct_list = []   # タコ
cross_list = [] # バツ印
for size in size_list:
    bin_tmp = cv2.imread('pbm\\lamp_ika_' + size + '.pbm', -1)
    ika_list.append(bin_tmp)
    bin_tmp = cv2.imread('pbm\\lamp_oct_' + size + '.pbm', -1)
    oct_list.append(bin_tmp)
    bin_tmp = cv2.imread('pbm\\lamp_cross_' + size + '.pbm', -1)
    cross_list.append(bin_tmp)


def listtop():
    ''' 記録リストの先頭行を返す '''
    list_top =  ['status_' + str(i) for i in range(8)]

    return list_top


def forFrameObjective(frame, team_color):
    ''' 俯瞰視点：フレームに対しての一連の処理を行う '''
    # ランプの大きさ
    lamp_size = getSizeObjective(frame)
    # 生存状況
    status_list = getStatusObjective(frame, team_color, lamp_size)

    return status_list


def forFrameSubjective(frame, team_color, shape_list):
    ''' 主観視点：フレームに対しての一連の処理を行う '''
    # ランプの大きさ
    lamp_size = getSizeSubjective(frame, team_color, shape_list)
    # 生存状況
    status_list = getStatusSubjective(frame, team_color, shape_list, lamp_size)

    return status_list


def getClosestIndex(list, num):
    ''' 最も近い値のインデックスを返す '''
    abs_list = np.abs(np.asarray(list) - num)
    index = abs_list.argmin()

    return index


def getTeamColor(frame):
    ''' 各チームの色を取得する '''
    # 各チームの色
    team_color = ['nodata', 'nodata']

    # アルファとブラボー
    for i in range(2):
        # 対象は4プレイヤー分のイカランプ
        TL = (L_lamp['MM'][0+4*i], T_lamp['subMM'])
        BR = (R_lamp['MM'][3+4*i], B_lamp['subMM'])
        # 最も面積を占める色をチームカラー候補から取得
        max_color = iip.getMostLargeColor(frame, TL, BR, color_catalog)
        # リストに記録
        team_color[i] = max_color

    return team_color


def getShape(frame, team_color):
    ''' イカランプの形を取得する '''
    # イカとタコの比較画像読み込み（LLサイズの切り抜き）
    bin_ika = cv2.imread('.\\pbm\\lamp_ika_MM.pbm', -1)
    bin_oct = cv2.imread('.\\pbm\\lamp_oct_MM.pbm', -1)
    tmp_list = [bin_ika, bin_oct]

    # 記録リスト
    shape_list = ['nodata' for i in range(8)]

    # 8プレイヤー分
    for i in range(8):
        # 基準色のインデックスはiが3以下は0、4以上は1
        idx = 0 if i<=3 else 1
        thd = team_color[idx]
        # イカランプ座標（中心はMM、大きさはLLの範囲）
        left   = C_lamp['MM'][i] - W_lamp['LL']
        right  = C_lamp['MM'][i] + W_lamp['LL']
        top    = T_lamp['subLL']
        bottom = B_lamp['subLL']
        TL = (left, top)
        BR = (right, bottom)
        # 一致率が大きい比較画像のインデックスを取得
        index = iip.getMostMatchImage(frame, TL, BR, tmp_list,
                                      threshold=thd, color_type='HSV')
        # インデックスを形名に反映
        shape = ['ika', 'oct'][index]
        # リストに記録
        shape_list[i] = shape

    return shape_list


def getSizeObjective(frame):
    ''' 俯瞰視点：ランプの大きさを取得する '''
    # ランプ大きさ SS, SM, MM, ML, LL
    lamp_size = ['nodata', 'nodata']

    # ブルーのBボタン位置の切り取り
    left,  top    = TL_button
    right, bottom = BR_button
    img_trm = frame[top:bottom, left:right]
    # 白で2値化
    bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])

    # ラベリング処理
    retval, labels, stats, cent = cv2.connectedComponentsWithStats(bin_trm)
    retval = retval - 1
    stats = np.delete(stats, 0, 0)
    # Bボタン部分を探す
    for index in range(retval):
        w = stats[index][2]
        h = stats[index][3]
        s = stats[index][4]
        # 縦横の平均値が判定値
        ave = (w+h)/2
        # 面積が閾値以上ならばボタン
        if s > thd_button:
            # 判定値がどのボタンの大きさに近いか
            idx = getClosestIndex(size_button, ave)
            # 大きさのインデックス == サイズ名インデックス
            lamp_size[0] = size_list[4-idx]
            lamp_size[1] = size_list[idx]

    return lamp_size


def getSizeSubjective(frame, team_color, shape_list):
    '''
    主観視点：ランプの大きさを取得する
    左から4番目を基準イカランプとしてその大きさを調べる
    '''
    # ランプ大きさ SS, SM, MM, ML, LL
    lamp_size = ['nodata', 'nodata']

    # ランプの形の画像
    tmp_list = ika_list if shape_list[3] == 'ika' else oct_list
    # 基準イカランプ切り出し
    top    = T_lamp['subLL']
    bottom = B_lamp['subLL']
    left   = L_lamp['LL'][3]
    right  = R_lamp['LL'][3]
    img_trm = frame[top:bottom, left:right]
    # BGR -> HSV
    hsv_trm = cv2.cvtColor(img_trm, cv2.COLOR_BGR2HSV)

    # 基準イカランプの状態を把握する
    # 基準色
    color_list = ['blk', team_color[0], 'spw']
    # LLの画像でマスクしてランプ外の影響を減らす
    bin_shp = tmp_list[4]
    # 抽出された面積が最も大きい色を探す
    s_max = 0
    color_max = 'nodata'
    bin_max = 0
    for color in color_list:
        # 閾値を取得
        thd_min, thd_max = thd_hsv[color]
        # 基準色で2値化
        bin_trm = cv2.inRange(hsv_trm, thd_min, thd_max)
        # マスク処理
        msk_trm = cv2.bitwise_and(bin_trm, bin_shp)
        # 抽出された部分の面積を取得
        s = cv2.countNonZero(msk_trm)

        if s >= s_max:
            s_max = s
            color_max = color
            bin_max = bin_trm

    # 黒以外の場合は状態取得で使った二値化画像を流用
    # 黒の場合はバツ印で大きさ判別するためグレーで二値化
    if color_max == 'blk':
        tmp_list = cross_list
        bin_max = cv2.inRange(img_trm, thd_rgb['gry'][0], thd_rgb['gry'][1])

    # 候補画像で一致率が最も高いものを探す
    val_max = 0
    index = 2
    for i, template in enumerate(tmp_list):
        # 一致率算出
        jug = cv2.matchTemplate(bin_max, template, cv2.TM_CCORR_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)

        if maxVal > val_max:
            val_max = maxVal
            index = i

    # 大きさのインデックス == サイズ名インデックス
    lamp_size[0] = size_list[index]
    lamp_size[1] = size_list[4-index]

    return lamp_size


def getStatusObjective(frame, team_color, lamp_size):
    ''' 俯瞰視点：イカランプの状態を取得する '''
    # 記録リスト 0:dead  1:alive  2:sp
    status_list = ['nodata' for i in range(8)]

    # 基準色リスト [黒, チームカラー, スペシャル状態]
    lamp_color = [['blk', color, 'spw'] for color in team_color]

    # 8プレイヤー分
    for i in range(8):
        # サイズなどのインデックスはiが3以下は0、4以上は1
        idx = 0 if i<=3 else 1
        # イカランプ座標
        left   = L_lamp[lamp_size[idx]][i]
        right  = R_lamp[lamp_size[idx]][i]
        top    = T_lamp['obj' + lamp_size[idx]]
        bottom = B_lamp['obj' + lamp_size[idx]]
        TL = (left, top)
        BR = (right, bottom)
        # 最も面積を占める色を取得
        max_color = iip.getMostLargeColor(frame, TL, BR, lamp_color[idx])
        # 最大の色のインデックス -> イカランプの状態
        status = lamp_color[idx].index(max_color)
        # リストに記録
        status_list[i] = status

    return status_list


def getStatusSubjective(frame, team_color, shape_list, lamp_size):
    ''' 主観視点：イカランプの状態を取得する '''
    # 記録リスト 0:dead  1:alive  2:sp
    status_list = ['nodata' for i in range(8)]

    # 基準色リスト [黒, チームカラー, スペシャル状態]
    lamp_color = [['blk', color, 'spw'] for color in team_color]

    # 8プレイヤー分
    for i in range(8):
        # サイズと色のインデックスはiが3以下は0、4以上は1
        idx = 0 if i<=3 else 1
        size = lamp_size[idx]
        thd = lamp_color[idx]
        # イカランプ座標
        left   = C_lamp[size][i] - W_lamp['LL']
        right  = C_lamp[size][i] + W_lamp['LL']
        top    = T_lamp['subLL']
        bottom = B_lamp['subLL']
        TL = (left, top)
        BR = (right, bottom)
        # イカランプの形の画像
        shape = shape_list[i]
        index = size_list.index(size)
        bin_shp = ika_list[index] if shape == 'ika' else oct_list[index]
        # 最も面積を占める色を取得
        max_color = iip.getMostLargeColor(frame, TL, BR, thd, mask=bin_shp)
        # 最大の色のインデックス -> イカランプの状態
        status = lamp_color[idx].index(max_color)
        # リストに記録
        status_list[i] = status

    return status_list


def getStatusMap(frame, team_color):
    '''
    主観視点マップ画面からプレイヤー状態を取得
    ※自分の状態は判別できない
    '''
    # 記録リスト 0:dead  1:alive  2:sp
    status_list = ['nodata' for i in range(7)]

    # 7プレイヤー分
    for i in range(7):
        # サイズなどのインデックスはiが2以下は0、3以上は1
        idx = 0 if i<=2 else 1
        # イカランプ座標
        TL = TL_map[i]
        BR = BR_map[i]
        # バツ印の一致率を算出
        val_crs = iip.getMatchValue(bin_crs[idx], frame, TL, BR,
                                    team_color[idx], 'hsv', 'mask')

        # 一致率が閾値以上ならたおされている
        if val_crs > thd_val:
            status = 0

        # 通常かスペシャル状態か
        else:
            # スペシャル状態で2値化
            val_spw = iip.getMatchValue(bin_spw[idx], frame, TL, BR,
                                        'spw', 'hsv', 'mask')
            # 閾値はちょっとゆるめに設定
            if val_spw > thd_val * 0.7:
                status = 2
            else:
                status = 1
        # 記録
        status_list[i] = status

    return status_list