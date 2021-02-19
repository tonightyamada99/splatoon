# -*- coding: utf-8 -*-

import cv2
import numpy as np
import ikaImageProcessing as iip

'''''''''''''''''''''''''''''''''''''''''''''''
カウント表示がガチエリアと同様のため
カウント・ペナルティカウントの数字認識は
zonesの名前のものを使用します
'''''''''''''''''''''''''''''''''''''''''''''''

# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# カウント表示 count window
T_cnt = [130, 150]  # [表示, 数字]
B_cnt = [204, 204]
L_cnt = [804, 1026] # [アルファ, ブラボー]
R_cnt = [894, 1116]
# ペナルティプラス
TL_pls = [(836, 222), (1010, 222)]
BR_pls = [(874, 250), (1048, 250)]
# ペナルティカウント
TL_pct = [(862, 216), (1037, 216)]
BR_pct = [(905, 256), (1080, 256)]
# アサリの数
T_clm = 141
B_clm = 186
L_clm = [516, 1342]
R_clm = [576, 1402]

# プラスの大きさの範囲
size_pls = [18, 23]     # @FHD(1920, 1080)

# 色閾値 threshold
# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), ( 64,  64,  64)],
           'wht':[(192, 192, 192), (255, 255, 255)]}


def listtop():
    ''' 記録リストの先頭行を返す '''
    list_top = ['control', 'count_alfa', 'count_bravo',
                'penalty_count_alfa', 'penalty_count_bravo',
                'clam_num_alfa', 'clam_num_bravo']

    return list_top


def forFrame(frame, team_color):
    ''' フレームに対しての一連の処理を行う '''
    # 確保状況
    control = getControl(frame, team_color)
    # カウント
    count_list = getCount(frame, team_color, control)
    # ペナルティカウントの有無
    judge_penalty = judgePenalty(frame)
    # ペナルティカウント
    pcount_list = getPenaltyCount(frame, judge_penalty)
    # アサリ保持数
    clam_list = getClam(frame)
    # 出力リスト
    out_list = [control] + count_list + pcount_list + clam_list

    return out_list



def getControl(frame, team_color):
    ''' ゴールの状況を取得する '''
    # ゴールの状況 in control -> 0:neutral 1:yellow 2:blue
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
                              threshold=color, color_type='HSV',resize='on')

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


def getClam(frame):
    ''' アサリ保持数を取得する '''
    # 記録リスト
    clam_list = [0, 0]

    # 数字画像読み込み
    image_num = []
    for num in range(10):
        num_path = '.\\pbm\\clam_' + str(num) + '.pbm'
        bin_num = cv2.imread(num_path, -1)
        image_num.append(bin_num)

    # 数字の高さと幅の最大最小を取得
    h_list = [image_num[i].shape[0] for i in range(10)]
    w_list = [image_num[i].shape[1] for i in range(10)]
    h_max, h_min = max(h_list), min(h_list)
    w_max, w_min = max(w_list), min(w_list)

    # アルファとブラボー
    for i in range(2):
        # アサリ数表示位置の切り取り
        t, l = T_clm, L_clm[i]
        b, r = B_clm, R_clm[i]
        img_trm = frame[t:b, l:r]
        # 白で二値化
        bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])

        # アサリの数は数字の大きさの幅が大きいため二値画像に余分な部分が多い
        # 数字は中央付近の白部分だけとなるためそのラベル数字を取得する
        # ラベリング処理
        retval, labels, stats, cent = cv2.connectedComponentsWithStats(bin_trm)
        # ラベル画像の中央部分を切り抜き
        h, w = bin_trm.shape
        t, l = round(h * 1/4), round(w * 1/4)
        b, r = round(h * 3/4), round(w * 3/4)
        label_trm = labels[t:b, l:r]

        # 切り抜いたラベル画像に含まれるラベル数字を取得（0は黒部分のため無視）
        label_list = []
        for num in range(1, retval):
            if num in label_trm:
                label_list.append(num)

        # 認識した数字の記録リスト
        num_list = []
        # 取得したラベル数字それぞれについて
        for label in label_list:
            # 各ラベルの座標と大きさ
            x = stats[label][0]
            y = stats[label][1]
            w = stats[label][2]
            h = stats[label][3]

            # 高さが小さいものは小数点やノイズ
            if h > h_min*0.9:
                # 対象を切り取り
                bin_tmp = bin_trm[y:y+h, x:x+w]

                # 対象をリサイズ
                scale = h_min / h
                bin_tmp = cv2.resize(bin_tmp, None, fx=scale, fy=scale)
                h, w = bin_tmp.shape

                # 対象を黒画像に貼り付け target
                # 数字ごとの大きさの違いに対応するため
                bin_tgt = np.zeros((h_max+4, w_max+4), dtype=np.uint8)
                bin_tgt[2:2+h, 2:2+w] = bin_tmp

                # 対象の数字を判別する
                num_tgt = 0
                val_tgt = 0

                # 0~9の数字画像で一致率が最も高いものを探す
                for num, bin_num in enumerate(image_num):
                    # 一致率算出
                    jug = cv2.matchTemplate(bin_tgt, bin_num, cv2.TM_CCOEFF_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)

                    if maxVal > val_tgt:
                        val_tgt = maxVal
                        num_tgt = num

                # リストに記録
                num_list.append([num_tgt, x])

        # 記録リストをx座標の大きい順（下の桁から上へ）にソート
        num_list.sort(key=lambda x: x[1], reverse=True)
        # ソートしたリストを数字に変換
        # 桁の小さい順に並んでいるので(数字)×10^(インデックス)で変換できる
        number = 0
        for index, [num, x] in enumerate(num_list):
            place = 10 ** index     # 桁:place
            number += num * place

        clam_list[i] = number

    return clam_list


def test():
    ''' 動作テスト '''

    for i in range(34):
        img_path = 'capture_image\\image_obj_clam_' + str(i).zfill(2) + '.png'
        frame = cv2.imread(img_path)

        print('====================================')
        print(img_path)

        import ikaLamp
        team_color = ikaLamp.getTeamColor(frame)

        data_list = frame(frame, team_color)

        print('====================================')
        print(img_path)
        print('control', data_list[0])
        print('count  ', data_list[1], data_list[2])
        print('pcount ', data_list[3], data_list[4])
        print('clam num', round(data_list[5], 3), round(data_list[6], 3))

        # プレビュー
        scale = 0.5
        img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
        cv2.imshow('Preview', img_rsz)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    test()
