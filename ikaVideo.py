# -*- coding: utf-8 -*-

import cv2
import csv
import os.path

import ikaLamp
import ikaTracking
import ikaColor


# 各プレイヤーのイカランプの位置
TL_lamp_n = [(518, 47), (629, 47), (709, 47), (792, 47), (1047, 47), (1130, 47), (1220, 47), (1311, 47)] 
BR_lamp_n = [(608, 92), (699, 92), (789, 92), (872, 92), (1127, 92), (1210, 92), (1290, 92), (1401, 92)]


# 対象動画
match = 'PL-DAY2_1-1'
player_list = [i for i in range(1, 9)]

frame_start = 1264
frame_end = 19436

# 何フレームごとに処理を行うか
frame_skip = 30

#あとみーのディレクトリ
video_path = 'C:\\Users\\nfkat\\Documents\\splatoon\\PremiereLeague\\' + match + '.mp4'
#video_path = 'D:\splatoon_movie\PremiereLeague\DAY2\\' + match + '.avi'
video_name, video_ext = os.path.splitext(os.path.basename(video_path))

out_video_path = video_name + '_test.avi'
csv_path = video_name + '_test2.csv'

# プレイヤーの周囲何ピクセルの色を取得するか
color_r = 50


def work():
    ''' 動画処理 '''
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # 以下フレーム処理結果の準備
    # 記録用のリスト
    list_top = []
    for i in range(len(player_list)):
        # イカランプ Dead or Alive
        list_top.append(str(player_list[i]) + '_doa' )
        # ポジション
        list_top.append(str(player_list[i]) + '_point_x')
        list_top.append(str(player_list[i]) + '_point_y')
        list_top.append(str(player_list[i]) + '_maxVal')

        # 周辺インク割合
        list_top.append(str(player_list[i]) + '_color_yellow')
        list_top.append(str(player_list[i]) + '_color_blue')
        list_top.append(str(player_list[i]) + '_color_other')
     
    record = [list_top]
        
    
    # ポジションの比較画像
    gray_all = [[]]  # index 0 はダミー
    for player_num in range(1,9):
        img_tmp = cv2.imread('PL-DAY2_1-1_name_' + str(player_num) + '.png', 0)
        gray_tmp = ikaTracking.nameBinarization(img_tmp, player_num)
        gray_all.append(gray_tmp)

    
    # 動画処理
    fcount = 0
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount += 1  
            
        if frame_start <= fcount < frame_end:
            if (fcount- frame_start) % frame_skip == 0:              
                # フレームに対しての処理
                # イカランプ用のピンチ判別
                danger_num = ikaLamp.judgeDanger(frame)
                
                # 記録用のリスト
                record_frame = []
                
                for player_num in player_list:
                    # イカランプ
                    doa, surf_list = ikaLamp.judgeLamp(frame, danger_num, player_num)
                    record_frame.append(doa)

                    # ポジション
                    gray_name = gray_all[player_num]
                    point_x, point_y, maxVal = ikaTracking.name(frame, gray_name, player_num)
                    # 座標は幅・高さで割って比率で記録
                    record_frame.append(point_x / W)
                    record_frame.append(point_y / H)
                    # 一致率（-1~1）を記録
                    record_frame.append(maxVal)
                    # 色
                    color = ikaColor.getColorRatio(frame, point_x, point_y, color_r)
                    record_frame.append(color[0])
                    record_frame.append(color[1])
                    record_frame.append(color[2])
                
                record.append(record_frame)
                
        if fcount == frame_end:
            break
                
    video.release

    # CSV出力
    with open(csv_path, 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(record)
        
        
def workOutputVideo():
    ''' 結果動画の出力も同時に行う '''        
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = video.get(cv2.CAP_PROP_FPS) / frame_skip 

    # 出力設定
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(out_video_path, fourcc, fps, (int(W), int(H)))
    
    # 以下フレーム処理結果の準備
    # 記録用のリスト
    list_top = []
    for i in range(len(player_list)):
        # イカランプ Dead or Alive
        list_top.append(str(player_list[i]) + '_doa' )
        # ポジション
        list_top.append(str(player_list[i]) + '_point_x')
        list_top.append(str(player_list[i]) + '_point_y')
        list_top.append(str(player_list[i]) + '_maxVal')
     
    record = [list_top]
        
    
    # ポジションの比較画像
    gray_all = [[]]  # index 0 はダミー
    for player_num in range(1,9):
        img_tmp = cv2.imread('PL-DAY2_1-1_name_' + str(player_num) + '.png', 0)
        gray_tmp = ikaTracking.nameBinarization(img_tmp, player_num)
        gray_all.append(gray_tmp)
    

    # 動画処理
    fcount = 0
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount += 1  
            
        if frame_start <= fcount < frame_end:
            if (fcount- frame_start) % frame_skip == 0:              
                # フレームに対しての処理
                # イカランプ用のピンチ判別
                danger_num = ikaLamp.judgeDanger(frame)
                
                # 記録用のリスト
                record_frame = []
                doa_list = []
                point_list = []
                
                for player_num in player_list:
                    # イカランプ
                    doa, surf_list = ikaLamp.judgeLamp(frame, danger_num, player_num)
                    record_frame.append(doa)
                    doa_list.append(doa)                    
                    # ポジション
                    gray_name = gray_all[player_num]
                    point_x, point_y, maxVal = ikaTracking.name(frame, gray_name)
                    # 座標は幅・高さで割って比率で記録
                    record_frame.append(point_x / W)
                    record_frame.append(point_y / H)
                    record_frame.append(maxVal)
                    point_list.append([point_x, point_y])
                
                record.append(record_frame)

                
                # 書き出し用の画像処理
                out_frame = frame
                               
                # イカランプ
                for i, player_num in enumerate(player_list):
                    doa = doa_list[i]
                    TL = TL_lamp_n[player_num - 1]
                    BR = BR_lamp_n[player_num - 1]
                    if doa == 0:
                        cv2.rectangle(out_frame, TL, BR, (255, 0, 255), 2)
                    elif doa == 1:
                        cv2.rectangle(out_frame, TL, BR, (255, 255, 0), 2)
                    elif doa == 2:
                        cv2.rectangle(out_frame, TL, BR, (0, 255, 255), 2)                

                # ポジション
                for i, player_num in enumerate(player_list):
                    point_x = point_list[i][0]
                    point_y = point_list[i][1]
                    TL = (point_x - 100, point_y - 44)
                    BR = (point_x + 100, point_y - 16)
                    
                    cv2.circle(out_frame, (point_x, point_y), 2, (255, 255, 0), -1)
                    cv2.rectangle(out_frame, TL, BR, (255, 255, 0), 2)
              
                    out.write(out_frame)
                    
    video.release
    out.release

    # CSV出力
    with open(csv_path, 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(record)
        
        

def main():
    ''' メイン処理 '''
    work()
    
    # workOutputVideo()
    
        
if __name__ == "__main__":
    main()