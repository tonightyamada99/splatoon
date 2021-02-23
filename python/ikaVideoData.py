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
meter_name = 'Data'.ljust(12, ' ')



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


def getData(video_path, overwrite=0):
    ''' 試合動画からカウントと生存状況を取得 '''
    # 動画の名前の取得
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    # 読み込みファイル
    info_path = video_dir + '\\' + video_name + '_info.csv'
    # 出力先
    status_path = video_dir + '\\' + video_name + '_status.csv'
    count_path = video_dir + '\\' + video_name + '_count.csv'

    if not os.path.exists(info_path):
        print('動画情報ファイルが見つかりません。')

    if os.path.exists(status_path) and os.path.exists(count_path) \
        and overwrite==0:
        print('データ取得済み')

    else:
        # 動画の情報を読み込む
        info_dict = csvread.readAsDict(info_path)
        viewpoint    = info_dict['viewpoint']

        # 視点に応じて動画処理
        if viewpoint == 'obj':
            status_list, count_list = forObjective(video_path, info_dict)
        elif viewpoint == 'sub':
            status_list, count_list = forSubjective(video_path, info_dict)

        # CSV出力
        with open(status_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(status_list)

        with open(count_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(count_list)


def forObjective(video_path, info_dict):
    ''' 俯瞰視点：試合のデータを取得する '''
    # 動画の情報を読み込む
    frame_all    = info_dict['frame_all']
    frame_start  = info_dict['frame_start']
    frame_end    = info_dict['frame_end']
    rule         = info_dict['rule']
    stage_num    = info_dict['stage_num']
    team_color_a = info_dict['team_color_alfa']
    team_color_b = info_dict['team_color_bravo']
    team_color = [team_color_a, team_color_b]

    # エリアの数を取得（ルールがエリア以外ならば0）
    zones_num = getZonesNum(rule, stage_num)

    # 記録リスト
    status_list = [['fcount'] + readListTop('lamp')]
    count_list  = [['fcount'] + readListTop(rule, zones_num)]

    # 動画読み込み
    video = cv2.VideoCapture(video_path)

    ### ここから動画処理 #####################################################
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
        printMeter(fcount, frame_all)

        # 試合中のフレームが対象
        if frame_start <= fcount < frame_end:
            # イカランプから状態を取得
            status_frame = ikaLamp.forFrameObjective(frame, team_color)

            # ルールごとの情報を取得
            if rule == 'zones':
                count_frame = ikaZones.frame(frame, zones_num, team_color)
            elif rule == 'tower':
                count_frame = ikaTower.frame(frame)
            elif rule == 'rain':
                count_frame = ikaRainmaker.frame(frame)
            elif rule == 'clam':
                count_frame = ikaClam.frame(frame)
            else:
                count_frame = []

            # 出力リストに記録
            status_list.append([fcount] + status_frame)
            count_list.append([fcount] + count_frame)

        elif fcount == frame_end:
            break

    video.release
    printMeter(frame_all, frame_all)
    ### ここまで動画処理 #####################################################

    return status_list, count_list


def forSubjective(video_path, info_dict):
    ''' 主観視点：試合のデータを取得する '''
    # 画面情報ファイル読み込み
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    screen_path = video_dir + '\\' + video_name + '_screen.csv'
    screen_list = csvread.readAsList(screen_path)

    # 動画の情報を読み込む
    frame_all    = info_dict['frame_all']
    frame_start  = info_dict['frame_start']
    frame_end    = info_dict['frame_end']
    rule         = info_dict['rule']
    stage_num    = info_dict['stage_num']
    team_color_a = info_dict['team_color_alfa']
    team_color_b = info_dict['team_color_bravo']
    user_num     = info_dict['user_num']
    team_color = [team_color_a, team_color_b]
    shape_list = [info_dict['shape_' + str(i+1)] for i in range(8)]

    # エリアの数を取得（ルールがエリア以外ならば0）
    zones_num = getZonesNum(rule, stage_num)

    # 記録リスト
    status_list = [['fcount'] + readListTop('lamp')]
    count_list  = [['fcount'] + readListTop(rule, zones_num)]
    # リストの幅
    width_list = len(count_list[0]) - 1

    # 動画読み込み
    video = cv2.VideoCapture(video_path)

    ### ここから動画処理 #####################################################
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
        printMeter(fcount, frame_all)

        # 試合中のフレームが対象
        if frame_start <= fcount < frame_end:
            # 画面状況取得
            idx = fcount - frame_start + 1
            screen_map = screen_list[idx][1]

            if screen_map == 0:
                # イカランプから状態を取得
                status_frame = ikaLamp.forFrameSubjective(frame,
                                                       team_color, shape_list)
                # ルールごとの情報を取得
                count_frame = getCount(frame, rule, zones_num, team_color)

            elif screen_map == 1:
                # マップ画面から状態を取得
                status_frame = ikaLamp.getStatusMap(frame, team_color)
                # プレイヤーの状態は把握できない
                status_frame.insert(user_num-1, 'nodata')

                # カウント等は取得できない
                count_frame = ['nodata' for i in range(width_list)]

            # 出力リストに記録
            status_list.append([fcount] + status_frame)
            count_list.append([fcount] + count_frame)

        elif fcount == frame_end:
            break

    video.release
    printMeter(frame_all, frame_all)
    ### ここまで動画処理 #####################################################

    return status_list, count_list


def getZonesNum(rule, stage_num):
    ''' リストをステージ番号で検索してガチエリアの数を取得する '''
    if rule == 'zones':
        stage_list = csvread.readAsList('stage.csv')
        for i in range(len(stage_list)):
            if stage_list[i][0] == stage_num:
                zones_num = stage_list[i][2]
                break
    else:
        zones_num = 0

    return zones_num


def readListTop(rule, zones_num=0):
    ''' 記録リストの先頭行を読み込む '''
    if rule == 'lamp':
        list_top = ikaLamp.listtop()
    elif rule == 'zones':
        list_top = ikaZones.listtop(zones_num)
    elif rule == 'tower':
        list_top = ikaTower.listtop()
    elif rule == 'rain':
        list_top = ikaRainmaker.listtop()
    elif rule == 'clam':
        list_top = ikaClam.listtop()
    else:
        list_top = []

    return list_top


def getCount(frame, rule, zones_num=0, team_color=[]):
    ''' ステージリストをステージ番号で検索してガチエリアの数を取得する '''
    if rule == 'zones':
        count_frame = ikaZones.forFrame(frame, zones_num, team_color)
    elif rule == 'tower':
        count_frame = ikaTower.forFrame(frame)
    elif rule == 'rain':
        count_frame = ikaRainmaker.forFrame(frame)
    elif rule == 'clam':
        count_frame = ikaClam.forFrame(frame, team_color)
    else:
        count_frame = []

    return count_frame


def main():
    ''' メイン処理 '''
    # ビデオディレクトリ取得 *はワイルドカード
    fnames = glob.glob('D:\\splatoon_movie\\capture\\video_sub_rain*.mp4' )

    for video_path in fnames:
        print('==================================================')
        print(os.path.basename(video_path))

        getData(video_path)

    print('==================================================')


if __name__ == "__main__":
    main()