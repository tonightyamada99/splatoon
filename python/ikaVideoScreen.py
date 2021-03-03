# -*- coding: utf-8 -*-

import cv2
import csv
import os.path

import csvread
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# ナイス
TL_nice = ( 68, 1016)
BR_nice = (132, 1048)
# 一致率の閾値 threshold
thd_val = 0.9
# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'sgn':[(224, 224, 224), (255, 255, 255)]}
# ナイス画像
bin_nice = cv2.imread('.\\pbm\\sign_nice.pbm', -1)

# 処理進捗メーター関連
meter_name = 'Screen'


def judgeNice(frame):
    ''' ナイス表示の判別 '''
    # 「ナイス」との一致率算出
    val = iip.getMatchValue(bin_nice, frame, TL_nice, BR_nice,
                            threshold=thd_rgb['sgn'], mask='mask')
    # 閾値以上ならばナイス表示
    judge = True if val > thd_val else False

    return judge, val


def getScreen(video_path, out_dir=None, overwrite=0):
    ''' 主観視点動画の画面状況を調べる '''
    # 動画の名前の取得
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    # 読み込みファイル
    info_path = video_dir + '\\' + video_name + '_info.csv'
    # 出力先
    out_dir = video_dir if not out_dir else out_dir
    out_path = out_dir + '\\' + video_name + '_screen.csv'

    if not os.path.exists(info_path):
        iip.printMeter(meter_name, 1, 1)
    elif os.path.exists(out_path) and overwrite==0:
        iip.printMeter(meter_name, 1, 1)
    else:
        # 動画読み込み
        video = cv2.VideoCapture(video_path)
        frame_all = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # 動画の情報を読み込む
        info_dict = csvread.readAsDict(info_path)
        frame_start = info_dict['frame_start']
        frame_end   = info_dict['frame_end']

        # 出力リスト
        screen_list = [['fcount', 'screen_map', 'maxVal']]

        ### ここから動画処理 #################################################
        fcount = 0
        while video.isOpened():

            # フレーム取得
            ret, frame = video.read()
            # フレーム取得できなかったら終了
            if not ret:
                break

            # フレームカウント
            fcount += 1
            # 処理進捗をコマンドラインに表示
            iip.printMeter(meter_name, fcount, frame_all)

            # 試合中のフレームを対象
            if frame_start <= fcount < frame_end:
                # 画面判別
                jug, val = judgeNice(frame)
                # ナイス表示がなければマップ画面
                screen_map = 0 if jug else 1
                # 出力リストに記録
                screen_list.append([fcount, screen_map, val])

            elif fcount == frame_end:
                break

        video.release
        iip.printMeter(meter_name, frame_all, frame_all)
        ### ここまで動画処理 #################################################

        # CSV出力
        with open(out_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(screen_list)

        return screen_list