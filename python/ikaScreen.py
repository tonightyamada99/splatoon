# -*- coding: utf-8 -*-

import cv2
import sys
import csv
import glob
import os.path

import csvread
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# ナイス
TL_nice = ( 68, 1016)
BR_nice = (132, 1048)

# 閾値 threshold
# 一致率
thd_val = 0.9

# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'sgn':[(192, 192, 192), (255, 255, 255)]}

# ナイス画像
bin_nice = cv2.imread('.\\pbm\\sign_nice.pbm', -1)

# 処理進捗メーター関連
length_meter = 20
meter_name = 'Screen Status'



def judgeNice(frame):
    ''' ナイス表示の判別 '''
    # 「ナイス」との一致率算出
    val = iip.getMatchValue(bin_nice, frame, TL_nice, BR_nice,
                            thd_rgb['sgn'], mask='mask')
    # 閾値以上ならばナイス表示
    judge = True if val > thd_val else False

    return judge



def printMeter(now, all):
    ''' 処理進捗をコマンドラインに表示する '''
    # 進捗を計算
    ratio = now / all
    # テキスト作成
    meter = ('#' * round(length_meter*ratio)).ljust(length_meter, ' ')
    text = '\r{} [{}] {:.2f}% '.format(meter_name, meter, ratio*100)

    # テキスト表示（sysで上書き）
    sys.stdout.flush()
    sys.stdout.write(text)



def getScreenStatus(video_path):
    ''' 主観視点動画の画面状況を調べる '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)

    status_path = video_dir + '\\' + video_name + '_status.csv'
    out_path    = video_dir + '\\' + video_name + '_screen.csv'

    if not (os.path.exists(status_path)):
        print('動画情報ファイルが見つかりません。先にikaMatchStatus.pyを実行してください。')

    elif os.path.exists(out_path):
        print('画面情報取得済み')

    else:
        # 動画読み込み
        video = cv2.VideoCapture(video_path)
        frame_all = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # 動画の情報を読み込む
        status_dict = csvread.readAsDict(status_path)
        frame_start = status_dict['frame_start']
        frame_end   = status_dict['frame_end']

        # 出力リスト
        screen_list = [['fcount', 'screen_map']]


        ### ここから動画処理 #################################################
        fcount = 0
        while(video.isOpened()):

            # フレーム取得
            ret, frame = video.read()
            # フレーム取得できなかったら終了
            if not ret:
                break

            # フレームカウント
            fcount += 1
            # 処理進捗をコマンドラインに表示
            printMeter(fcount, frame_all)

            # 試合中のフレームを対象
            if frame_start <= fcount < frame_end:
                # 画面判別
                jug = judgeNice(frame)
                # ナイス表示がなければマップ画面
                screen_map = 0 if jug else 1
                # 出力リストに記録
                screen_list.append([fcount, screen_map])

            elif fcount == frame_end:
                break

        video.release
        printMeter(frame_all, frame_all)
        ### ここまで動画処理 #################################################

        # CSV出力
        with open(out_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(screen_list)


        return screen_list



def main():
    ''' メイン処理 '''
    # ビデオディレクトリ取得 *はワイルドカード
    fnames = glob.glob('.\\capture_movie\\movie*.avi' )

    for video_path in fnames:
        print('==================================================')
        print(os.path.basename(video_path))

        screen_list = getScreenStatus(video_path)

    print('==================================================')



if __name__ == '__main__':
    main()



