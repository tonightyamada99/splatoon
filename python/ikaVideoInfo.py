# -*- coding: utf-8 -*-

import cv2
import csv
import os.path

import csvread
import ikaLamp
import ikaRule
import ikaStage
import ikaStartEnd
import ikaImageProcessing as iip


# 処理メーターの名前
meter_name = 'Infomation'

# 視点指定のウィンドウ関連
name_window = 'Select Viewpoint and Player Number'
name_track_1 = 'Viewpoint'
name_track_2 = 'User Num'
width_window = 960


def selectViewpoint(frame):
    ''' 視点とプレイヤー位置を指定するウインドウを作る '''
    # 説明文画像
    img_how = cv2.imread('jpg\\videoinfo_viewpoint.jpg')
    H, W = img_how.shape[:2]
    scale = width_window / W
    rsz_how = cv2.resize(img_how, None, fx=scale, fy=scale)

    # フレーム画像リサイズ
    H, W = frame.shape[:2]
    scale = width_window / W
    rsz_frm = cv2.resize(frame, None, fx=scale, fy=scale)

    # 最初にウィンドウを生成
    cv2.namedWindow(name_window)

    # 画像表示
    img_prv = cv2.vconcat([rsz_how, rsz_frm])
    cv2.imshow(name_window, img_prv)

    # トラックバーのコールバック関数は何もしない空の関数
    def nothing(x):
        pass

    # トラックバーを生成
    cv2.createTrackbar(name_track_1, name_window, 1, 1, nothing)
    cv2.createTrackbar(name_track_2, name_window, 1, 4, nothing)

    # ESCが押されるまでループ
    while True:
        k = cv2.waitKey()
        if k == 27:
            # トラックバーの値を取得
            vp_num   = cv2.getTrackbarPos(name_track_1, name_window)
            user_num = cv2.getTrackbarPos(name_track_2, name_window)

            if vp_num == 0:
                viewpoint = 'obj' # 俯瞰:objective
                user_num = 0
            elif vp_num == 1:
                viewpoint = 'sub' # 主観:subjective

            # 終了
            cv2.destroyAllWindows()
            break

    return viewpoint, user_num


def getinfo(video_path, out_dir=None, overwrite=0):
    ''' 試合動画の情報を取得する '''
    # 動画の名前の取得
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    # 出力先
    out_dir = video_dir if not out_dir else out_dir
    out_path = out_dir + '\\' + video_name + '_info.csv'

    # 取得状況の把握
    if os.path.exists(out_path) and overwrite==0:
        iip.printMeter(meter_name, 1, 1)
        info_list = csvread.readAsList(out_path)
    else:
        # 動画読み込み
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_all = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # 取得する変数たち
        frame_rule  = 0
        rule        = 'nodata'
        stage_num   = 0
        frame_start = 0
        frame_end   = 0
        viewpoint   = 'nodata'
        user_num    = 0

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

            if frame_rule == 0:
                # ルール表示の判定
                jug_frame = ikaRule.judgeRule(frame)
                if jug_frame:
                    # 「ル」が表示されてから1秒後が判定フレーム
                    # エフェクトによってルール名などが表示されていないため
                    frame_rule = fcount + round(fps*1)

            elif fcount == frame_rule:
                # ルール取得
                rule = ikaRule.getRule(frame)
                # ステージ取得
                stage_num = ikaStage.getStage(frame)

            elif frame_start == 0:
                # 試合開始の判定
                if rule == 'turf':
                    jug_start = ikaStartEnd.judgeStartTurf(frame)
                else:
                    jug_start = ikaStartEnd.judgeStartGachi(frame)

                if jug_start:
                    # 試合開始は1秒前
                    # 試合開始ピッタリは時計表示がなくて認識できない
                    frame_start = fcount - round(fps*1)
                    # チームカラーの取得
                    team_color = ikaLamp.getTeamColor(frame)
                    # 視点の取得
                    # viewpoint, user_num = 'obj', 0
                    viewpoint, user_num = selectViewpoint(frame)
                    # イカランプの形の取得
                    if viewpoint == 'sub':
                        shape_list = ikaLamp.getShape(frame, team_color)
                    else:
                        shape_list = ['nodata' for i in range(8)]

            elif frame_end == 0:
                # 試合終了の判定
                jug_end = ikaStartEnd.judgeEnd(frame)
                if jug_end:
                    frame_end = fcount

            else:
                break

        video.release
        iip.printMeter(meter_name, frame_all, frame_all)
        ### ここまで動画処理 #################################################

        # リスト先頭行
        list_top = ['fps', 'frame_all', 'frame_start', 'frame_end',
                    'viewpoint', 'rule', 'stage_num',
                    'team_color_alfa', 'team_color_bravo', 'user_num']
        list_top += ['shape_' + str(i+1) for i in range(8)]
        # リスト内容 contents
        list_con = [fps, frame_all, frame_start, frame_end,
                    viewpoint, rule, stage_num,
                    team_color[0], team_color[1], user_num]
        list_con += shape_list
        # 出力リスト
        info_list = [list_top, list_con]

        # CSV出力
        with open(out_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(info_list)

    return info_list