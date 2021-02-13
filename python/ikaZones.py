# -*- coding: utf-8 -*-

import cv2
import numpy as np
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# カウント表示 count window
T_cnt = [134, 154]  # [表示, 数字]
B_cnt = [208, 208]
L_cnt = [804, 1026] # [アルファ, ブラボー]
R_cnt = [894, 1116]
# ペナルティプラス
TL_pls = [(836, 226), (1010, 226)]
BR_pls = [(874, 254), (1048, 254)]
# ペナルティカウント
TL_pct = [(862, 220), (1037, 220)]
BR_pct = [(905, 260), (1080, 260)]
# エリア塗り状況
T_rto = [158, 144, 197]
B_rto = [194, 174, 227]
L_rto = 916
R_rto = 1004

# プラスの大きさの範囲
size_pls = [18, 23]     # @FHD(1920, 1080)

# 色閾値 threshold
# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), ( 64,  64,  64)],
           'wht':[(192, 192, 192), (255, 255, 255)]}

# HSV[min, max](0~179, 0~255, 0~255)
thd_hsv = {'blk':[(  0,   0,   0), (179, 255, 128)],
           'wht':[(  0,   0, 192), (179, 128, 255)],
           'yel':[( 20, 128, 128), ( 30, 255, 255)],
           'blu':[(125, 128, 128), (135, 255, 255)]}


def listTop(zones_num):
    ''' 記録リストの先頭行を返す '''
    list_top = ['control', 'count_alfa', 'count_bravo',
                'penalty_count_alfa', 'penalty_count_bravo',
                'ratio_1_alfa', 'ratio_1_bravo']
    if zones_num == 2:
        list_top += ['ratio_2_alfa', 'ratio_2_bravo']

    return list_top


def frame(frame, zones_num, team_color):
    ''' フレームに対しての一連の処理を行う '''
    # 確保状況
    control = getControl(frame, team_color)
    # カウント
    count_list = getCount(frame, team_color, control)
    # ペナルティカウントの有無
    judge_penalty = judgePenalty(frame)
    # ペナルティカウント
    pcount_list = getPenaltyCount(frame, judge_penalty)
    # エリア塗り割合
    ratio_list = getRatio(frame, zones_num, team_color)
    # 出力リスト
    out_list = [control] + count_list + pcount_list + ratio_list

    return out_list


def getControl(frame, team_color):
    ''' エリアの確保状況を取得する '''
    # エリアの確保状況 in control -> 0:neutral 1:alfa 2:bravo
    control = 0

    # アルファとブラボー
    for i in range(2):
        # 色候補：通常は黒、確保中はチームカラー
        color_list = ['blk', team_color[i]]
        # カウント表示位置
        TL = (L_cnt[i], T_cnt[0])
        BR = (R_cnt[i], B_cnt[0])
        # 最も面積を占める色を色候補から取得
        max_color = iip.getMostLargeColor(frame, TL, BR, color_list)
        # チームカラーと同じ色なら確保中
        if max_color == team_color[i]:
            control = i+1

    return control


def getCount(frame, team_color, control):
    ''' カウントを取得する '''
    # 記録リスト
    count_list = ['nodata', 'nodata']

    # アルファとブラボー
    for i in range(2):
        ab = ['alfa', 'bravo'][i]

        # 数字画像読み込み
        image_num = []
        for num in range(10):
            num_path = '.\\pbm\\zones_' + ab + '_' + str(num) + '.pbm'
            bin_num = cv2.imread(num_path, -1)
            image_num.append(bin_num)

        # 数字の色は通常はチームカラー、確保中は白
        color = team_color[i] if control != i+1 else 'wht'
        # カウント表示位置
        TL = (L_cnt[i], T_cnt[1])
        BR = (R_cnt[i], B_cnt[1])
        # カウント数字取得
        count = iip.getNumber(frame, TL, BR, image_num,
                              threshold=color, color_type='HSV', resize='on')
        # リストに記録
        count_list[i] = count

    return count_list


def judgePenalty(frame):
    ''' ペナルティカウントの有無を判別する '''
    # 記録リスト
    judge_list = [False, False]

    # アルファとブラボー
    for i in range(2):
        # プラス表示位置切り取り
        left,  top    = TL_pls[i]
        right, bottom = BR_pls[i]
        img_trm = frame[top:bottom, left:right]
        # 白で二値化
        bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])
        # ラベリング処理
        retval, labels, stats, cent = cv2.connectedComponentsWithStats(bin_trm)
        retval = retval - 1
        stats = np.delete(stats, 0, 0)

        # 各ラベルの幅と高さを取得
        for index in range(retval):
            w = stats[index][2]
            h = stats[index][3]

            # 縦横の差が小さく、平均が閾値以内ならばプラス表示
            dif = abs(w-h)
            ave = (w+h)/2
            if dif <= 2 and size_pls[0] <= ave <= size_pls[1]:
                # プラス表示 -> ペナルティあり
                judge_list[i] = True

    return judge_list


def getPenaltyCount(frame, jug_pena):
    ''' ペナルティカウントを取得する '''
    # 記録リスト
    pcount_list = [0, 0]

    # アルファとブラボー
    for i in range(2):
        # ペナルティカウントがあれば
        if jug_pena[i]:

            # 数字画像読み込み
            image_num = []
            for num in range(10):
                num_path = '.\\pbm\\zones_pena_' + str(num) + '.pbm'
                bin_num = cv2.imread(num_path, -1)
                image_num.append(bin_num)

            # ペナルティカウント表示位置
            TL = TL_pct[i]
            BR = BR_pct[i]
            # カウント数字取得
            color = thd_rgb['wht']
            count = iip.getNumber(frame, TL, BR, image_num,
                                  threshold=color, resize='on')
            # リストに記録
            pcount_list[i] = count

    return pcount_list


def getRatio(frame, zones_num, team_color):
    ''' エリアの塗り割合を取得する '''
    # 記録リスト
    ratio_list = []

    # エリアの数で位置座標のインデックスを設定
    index_list = [[], [0], [1, 2]][zones_num]
    # 色
    color_list = team_color + ['blk']

    for index in index_list:
        # エリア塗り状況表示の切り取り
        top    = T_rto[index]
        bottom = B_rto[index]
        left   = L_rto
        right  = R_rto
        img_trm = frame[top:bottom, left:right]
        # BGR -> HSV
        hsv_trm = cv2.cvtColor(img_trm, cv2.COLOR_BGR2HSV)

        # 色ごとに面積を計算 [alfa, bravo, neutral]
        surf_list = [0, 0, 0]
        for i, color in enumerate(color_list):
            # 二値化
            bin_trm = cv2.inRange(hsv_trm, thd_hsv[color][0], thd_hsv[color][1])
            # 抽出された部分の面積を取得
            s = cv2.countNonZero(bin_trm)
            # 記録
            surf_list[i] = s

        # 総面積
        surf_sum = sum(surf_list)
        # 塗り割合を計算
        # 0で割ってはいけない
        if surf_sum != 0:
            for i in range(2):
                # 割合を計算してリストに記録
                r = surf_list[i] / surf_sum
                ratio_list.append(r)
        else:
            # 総面積が0ならば0を記録しておく
            ratio_list += [0, 0]

    return ratio_list


def test():
    ''' 動作テスト '''

    for i in range(35):
        img_path = 'capture_image\\image_obj_zones_' + str(i).zfill(2) + '.png'
        frame = cv2.imread(img_path)

        import ikaLamp
        team_color = ikaLamp.getTeamColor(frame)

        zones_num = 1
        data_list = frame(frame, zones_num, team_color)

        print('====================================')
        print(img_path)
        print('control', data_list[0])
        print('count  ', data_list[1], data_list[2])
        print('pcount ', data_list[3], data_list[4])
        print('ratio1 ', round(data_list[5], 3), round(data_list[6], 3))
        if zones_num == 2:
            print('ratio1 ', round(data_list[7], 3), round(data_list[8], 3))

        # プレビュー
        scale = 0.5
        img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
        cv2.imshow('Preview', img_rsz)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    test()
