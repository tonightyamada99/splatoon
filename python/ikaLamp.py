# -*- coding: utf-8 -*-

import cv2
import glob
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
L_lamp = {'SS':[570, 646, 721, 797, 1049, 1125, 1200, 1276],
          'SM':[554, 635, 715, 796, 1049, 1129, 1210, 1291],
          'MM':[536, 622, 708, 794, 1046, 1132, 1218, 1304],
          'ML':[518, 609, 700, 792, 1045, 1136, 1228, 1319],
          'LL':[498, 596, 692, 789, 1042, 1138, 1236, 1332]}
# 右
R_lamp = {'SS':[642, 718, 793, 869, 1121, 1197, 1272, 1348],
          'SM':[628, 709, 789, 870, 1123, 1203, 1284, 1365],
          'MM':[614, 700, 786, 872, 1124, 1210, 1296, 1382],
          'ML':[600, 691, 782, 874, 1127, 1218, 1310, 1401],
          'LL':[586, 684, 780, 877, 1130, 1226, 1324, 1420]}
# 中立状態（将来的に削除）
L_lamp_n = [518, 629, 709, 792, 1047, 1130, 1220, 1311]
R_lamp_n = [608, 699, 789, 872, 1127, 1210, 1290, 1401]
# 主観視点でのイカランプ上端座標
thd_ika = [17, 19, 21, 23, 26]
thd_oct = []

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

# 閾値 threshold
# 一致率
thd_val = 0.9

# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), (128, 128, 128)],
           'wht':[(128, 128, 128), (255, 255, 255)]}

# HSV[min, max](0~179, 0~255, 0~255)
thd_hsv = {'blk':[(  0,   0,   0), (179,  64, 128)],    # 黒
           'wht':[(  0,   0, 128), (179,  64, 255)],    # 白
           'spw':[(  0,  16, 128), (179, 128, 255)],    # スペシャル状態
           'yel':[( 20, 128, 128), ( 30, 255, 255)],
           'blu':[(125, 128, 128), (135, 255, 255)]}

# チームカラー候補
color_catalog = ['yel', 'blu']

# 比較画像
# バツ印:cross  味方:good guys  相手:bad guys
bin_ggc = cv2.imread('.\\pbm\\map_gg_cross.pbm', -1)
bin_bgc = cv2.imread('.\\pbm\\map_bg_cross.pbm', -1)
# スペシャル状態:special weapon
bin_ggs = cv2.imread('.\\pbm\\map_gg_spw.pbm', -1)
bin_bgs = cv2.imread('.\\pbm\\map_bg_spw.pbm', -1)
# 比較画像リスト
bin_crs  = [bin_ggc, bin_bgc]
bin_spw  = [bin_ggs, bin_bgs]


def listtop():
    ''' 記録リストの先頭行を返す '''
    list_top =  ['status_' + str(i) for i in range(8)]

    return list_top


def frameObjective(frame, team_color):
    ''' 俯瞰視点:フレームに対しての一連の処理を行う '''
    # ランプの大きさ
    lamp_size = getSizeObjective(frame)
    # 生存状況
    lamp_list = getStatus(frame, team_color, 'obj', lamp_size)

    return lamp_list


def frameSubjective(frame, team_color):
    ''' 主観視点:フレームに対しての一連の処理を行う '''
    # ランプの大きさ
    lamp_size = getSizeSubjective(frame)
    # 生存状況
    lamp_list = getStatus(frame, team_color, 'sub', lamp_size)

    return lamp_list


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
    # イカとタコの比較画像読み込み
    bin_ika = cv2.imread('.\\pbm\\ikalamp_ika.pbm', -1)
    bin_oct = cv2.imread('.\\pbm\\ikalamp_oct.pbm', -1)
    tmp_list = [bin_ika, bin_oct]

    # 記録リスト
    shape_list = ['nodata' for i in range(8)]

    # 8プレイヤー分
    for i in range(8):
        # 基準色のインデックスはiが3以下は0、4以上は1
        idx = 0 if i<=3 else 1
        thd = team_color[idx]
        # イカランプ座標
        TL = (L_lamp['MM'][i], T_lamp['subMM'])
        BR = (R_lamp['MM'][i], B_lamp['subMM'])
        # 一致率が大きい比較画像を取得
        tmp_index = iip.getMostMatchImage(frame, TL, BR, tmp_list,
                                          threshold=thd, color_type='HSV')
        # インデックスを形名に反映
        shape = ['ika', 'oct'][tmp_index]
        # リストに記録
        shape_list[i] = shape

    return shape_list


def getSizeSubjective(frame):
    ''' 主観：ランプの大きさを取得する '''
    # ランプ大きさ SS, SM, MM, ML, LL
    lamp_size = ['nodata', 'nodata']

    #############
    # 作成中... #
    #############

    return lamp_size


def getSizeObjective(frame):
    ''' 俯瞰：ランプの大きさを取得する '''
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


def getStatus(frame, team_color, viewpoint, lamp_size):
    ''' イカランプの状態を取得する '''
    # 記録リスト 0:dead  1:alive  2:sp
    lamp_list = ['nodata' for i in range(8)]

    # 基準色リスト [黒, チームカラー, スペシャル状態]
    lamp_color = [['blk', color, 'spw'] for color in team_color]

    # 8プレイヤー分
    for i in range(8):
        # サイズなどのインデックスはiが3以下は0、4以上は1
        idx = 0 if i<=3 else 1
        # イカランプ座標
        left   = L_lamp[lamp_size[idx]][i]
        right  = R_lamp[lamp_size[idx]][i]
        top    = T_lamp[viewpoint + lamp_size[idx]]
        bottom = B_lamp[viewpoint + lamp_size[idx]]
        TL = (left, top)
        BR = (right, bottom)
        # 最も面積を占める色を取得
        max_color = iip.getMostLargeColor(frame, TL, BR, lamp_color[idx])
        # 最大の色のインデックス -> イカランプの状態
        status = lamp_color[idx].index(max_color)
        # リストに記録
        lamp_list[i] = status

    return lamp_list


def getStatusMap(frame, team_color):
    '''
    主観視点マップ画面からプレイヤー状態を取得
    ※自分の状態は判別できない
    '''
    # 記録リスト 0:dead  1:alive  2:sp
    lamp_list = ['nodata' for i in range(7)]

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
            doa = 0

        # 通常かスペシャル状態か
        else:
            # スペシャル状態で2値化
            val_spw = iip.getMatchValue(bin_spw[idx], frame, TL, BR,
                                        'spw', 'hsv', 'mask')
            # 閾値はちょっとゆるめに設定
            if val_spw > thd_val * 0.7:
                doa = 2
            else:
                doa = 1
        # 記録
        lamp_list[i] = doa

    return lamp_list


def test():
    ''' 動作テスト '''

    viewpoint = 'sub'
    rule = 'zones'
    target_name = 'image_' + viewpoint + '_' + rule + '_02.png'

    img_dir = 'capture_image\\'
    target_path = img_dir + target_name
    fnames = glob.glob(target_path)

    for img_path in fnames:
        frame = cv2.imread(img_path)
        print('====================================')
        print(img_path[len(img_dir):])

        # 俯瞰視点
        if viewpoint == 'obj':
            team_color = getTeamColor(frame)
            print('team_color', team_color)

            lamp_size = getSizeObjective(frame)
            print('lamp_size ', lamp_size)

            lamp_list = getStatus(frame, team_color, viewpoint, lamp_size)
            print('lamp_list ', lamp_list)

        # 主観視点
        elif rule != 'map':
            team_color = getTeamColor(frame)
            print('team_color', team_color)

            shape_list = getShape(frame, team_color)
            print(shape_list[0:4])
            print(shape_list[4:8])

            # danger_num = judgeDanger(frame)
            # print('danger_num', danger_num)

            # lamp_list = getStatus(frame, team_color, viewpoint, lamp_size)
            # print('lamp_list ', lamp_list)

        # マップ画面
        else:
            team_color = ['yel', 'blu']
            # team_color = ['blu', 'yel']
            map_list = getStatusMap(frame, team_color)
            print(map_list)


        # プレビュー
        scale = 0.5
        img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)

        cv2.imshow('Preview', img_rsz)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    test()