# -*- coding: utf-8 -*-

import cv2
import csv
import sys
import glob
import os.path
import csvread

import ikaLamp
import ikaZones
import ikaTower
import ikaRainmaker
import ikaClam


# 処理進捗メーター関連
length_meter = 20
meter_name = 'Match Data'

# 何フレームごとに処理を行うか
frame_skip = 1


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


def getData(video_path):
    ''' 試合動画からカウントと生存状況を取得 '''
    # 動画の名前の取得
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    # 読み込みファイル
    status_path = video_dir + '\\' + video_name + '_status.csv'
    screen_path = video_dir + '\\' + video_name + '_screen.csv'
    # 出力先
    lamp_path = video_dir + '\\' + video_name + '_lamp.csv'
    count_path = video_dir + '\\' + video_name + '_count.csv'

    if not os.path.exists(status_path):
        print('動画情報ファイルが見つかりません。')

    if os.path.exists(lamp_path) and os.path.exists(count_path):
        print('データ取得済み')

    else:
        # 動画の情報を読み込む
        status_list = csvread.readAsDict(status_path)
        frame_all    = status_list[1][1]
        frame_start  = status_list[1][2]
        frame_end    = status_list[1][3]
        viewpoint    = status_list[1][4]
        rule         = status_list[1][5]
        stage_num    = status_list[1][6]
        zones_num    = status_list[1][7]
        team_color_a = status_list[1][8]
        team_color_b = status_list[1][9]
        user_num     = status_list[1][10]

        team_color = [team_color_a, team_color_b]


        # 出力リストの準備
        # 生存状況
        lamp_top = list_top['lamp']
        lamp_list = [lamp_top]

        # カウント
        if rule == 'zones':
            count_top = list_top[rule + str(zones_num)]
        else:
            count_top = list_top[rule]

        count_list = [count_top]


        # 動画処理はここから
        # 俯瞰視点
        if viewpoint == 'obj':
            # 動画読み込み
            video = cv2.VideoCapture(video_path)

            fcount = 0
            while(video.isOpened()):
                ret, frame = video.read()

                if not ret:
                    break

                fcount += 1

                # 進行状況をコマンドラインに表示
                sys.stdout.flush()
                sys.stdout.write("\r{}% Done ".format(round(fcount/frame_all*100, 2)))


                if frame_start <= fcount < frame_end:
                    # フレームに対しての処理
                    # イカランプの状態取得
                    lamp_frame = processLamp(frame, team_color)

                    # ルールごとの情報取得
                    if rule == 'zones':
                        count_frame = processZones(frame, zones_num)
                    elif rule == 'tower':
                        count_frame = processTower(frame)
                    elif rule == 'rain':
                        count_frame = processRainmaker(frame)
                    elif rule == 'clam':
                        count_frame = processClam(frame)
                    else:
                        count_frame = [0, 0]

                    # 出力リストに記録
                    lamp_list.append([fcount] + lamp_frame)
                    count_list.append([fcount] + count_frame)


                elif fcount == frame_end:
                    break

            video.release




        # CSV出力
        with open(lamp_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(lamp_list)

        with open(count_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(count_list)


        sys.stdout.flush()
        sys.stdout.write("\r100.00% Done")

        print('\n取得完了')






def correctCountList(video_path):
    ''' カウントの修正 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)

    status_path = video_dir + '\\' + video_name + '_status.csv'

    if not (os.path.exists(status_path)):
        print('動画のカウントファイルが見つかりません。')

    else:
        # 動画の情報を読み込む
        status_list = csvread.csvread(status_path)
        rule         = status_list[1][5]
        zones_num    = status_list[1][7]

        if rule == 'zones':
            count_path = video_dir + '\\' + video_name + '_count.csv'
            read_list = csvread.csvread(count_path)

            # カウントの補正
            count_list = []
            for i in range(1, len(read_list)):
                count = int(read_list[i][2])
                count_list.append(count)

            cor_count_y = ikaZones.correctCountList(count_list)

            count_list = []
            for i in range(1, len(read_list)):
                count = int(read_list[i][3])
                count_list.append(count)

            cor_count_b = ikaZones.correctCountList(count_list)

            # ペナルティカウントの補正
            pena_list = []
            pcount_list = []
            for i in range(1, len(read_list)):
                pena    = int(read_list[i][4])
                pcount  = int(read_list[i][6])
                pena_list.append(pena)
                pcount_list.append(pcount)

            cor_pcount_y = ikaZones.correctPenaltyCountList(pena_list, pcount_list)

            pena_list = []
            pcount_list = []
            for i in range(1, len(read_list)):
                pena    = int(read_list[i][5])
                pcount  = int(read_list[i][7])
                pena_list.append(pena)
                pcount_list.append(pcount)

            cor_pcount_b = ikaZones.correctPenaltyCountList(pena_list, pcount_list)


            # 補正したリストを保存
            list_top = read_list[0]
            cor_count_list = [list_top]
            for i in range(1, len(read_list)):

                fcount  = int(read_list[i][0])
                ctrl    = int(read_list[i][1])
                count_y = cor_count_y[i-1]
                count_b = cor_count_b[i-1]
                pena_y  = int(read_list[i][4])
                pena_b  = int(read_list[i][5])
                pena_count_y = cor_pcount_y[i-1]
                pena_count_b = cor_pcount_b[i-1]
                ratio_1_y    = float(read_list[i][8])
                ratio_1_b    = float(read_list[i][9])


                if zones_num == 1:
                    record = [fcount, ctrl, count_y, count_b, pena_y, pena_b, pena_count_y, pena_count_b, ratio_1_y, ratio_1_b]

                elif zones_num == 2:
                    ratio_2_y    = float(read_list[i][10])
                    ratio_2_b    = float(read_list[i][11])
                    record = [fcount, ctrl, count_y, count_b, pena_y, pena_b,
                              pena_count_y, pena_count_b, ratio_1_y, ratio_1_b, ratio_2_y, ratio_2_b]

                cor_count_list.append(record)

            out_path = video_dir + '\\' + video_name + '_count_cor.csv'
            with open(out_path, 'w') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerows(cor_count_list)


def main():
    ''' メイン処理 '''
    for i in [8]:
        # ビデオディレクトリ取得 '*'はワイルドカード
        fnames = glob.glob('.\\capture_movie\\movie_turf_1.avi' )

        for video_path in fnames:
            video_name = os.path.basename(video_path)

            print('=========================')
            print(video_name)

            getData(video_path)

            # correctCountList(video_path)





if __name__ == "__main__":
    main()