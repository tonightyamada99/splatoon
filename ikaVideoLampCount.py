# -*- coding: utf-8 -*-

import cv2
import csv
import glob
import os.path
import csvread

import ikaLamp
import ikaTracking
import ikaColor
import ikaZones
import ikaTower
import ikaRainmaker
import ikaClam


# 各プレイヤーのイカランプの位置
TL_lamp_n = [(518, 47), (629, 47), (709, 47), (792, 47), (1047, 47), (1130, 47), (1220, 47), (1311, 47)] 
BR_lamp_n = [(608, 92), (699, 92), (789, 92), (872, 92), (1127, 92), (1210, 92), (1290, 92), (1401, 92)]


# 対象動画
match = 'PL-DAY2_1-1'
player_list = [i for i in range(1, 9)]

frame_start = 1264
frame_end = 19436

# 何フレームごとに処理を行うか
frame_skip = 1

#あとみーのディレクトリ
video_path = 'C:\\Users\\nfkat\\Documents\\splatoon\\PremiereLeague\\' + match + '.mp4'
#video_path = 'D:\splatoon_movie\PremiereLeague\DAY2\\' + match + '.avi'
video_name, video_ext = os.path.splitext(os.path.basename(video_path))

out_video_path = video_name + '_test.avi'
csv_path = video_name + '_test2.csv'

# プレイヤーの周囲何ピクセルの色を取得するか
color_r = 50



def processLamp(frame):
    ''' イカランプのフレーム処理 '''
    # ピンチ判別
    danger_num = ikaLamp.judgeDanger(frame)
    
    # イカランプの状態
    return_list = []
    for player_num in player_list:
        doa, surf_list = ikaLamp.judgeLamp(frame, danger_num, player_num)
        return_list.append(doa)
        

    return return_list 



def processZones(frame, zones_num):
    ''' ガチエリアのフレーム処理 '''
    # エリア確保状況
    zones_ctrl = ikaZones.getControlTeam(frame)
    
    # カウント
    count = ikaZones.getCount(frame, zones_ctrl)
    
    # ペナルティカウント
    pena_list, pcount_list = ikaZones.getPenaltyCount(frame)
    
    # 塗り割合
    zones_ratio = ikaZones.getRatio(frame, zones_num)
  
    # 出力リストに記録
    return_list =  [zones_ctrl] + count + pena_list + pcount_list + zones_ratio
    
    
    return return_list



def processTower(frame):
    ''' ガチヤグラのフレーム処理 '''
    # ガチヤグラの確保状況と位置
    tower_ctrl, loc_ratio = ikaTower.getLocation(frame)   
    
    # カウント
    count = ikaTower.getCount(frame)
    
    # 出力リストに記録
    return_list = tower_ctrl + count + loc_ratio
    
    
    return return_list



def processRainmaker(frame):
    ''' ガチホコバトルのフレーム処理 '''
    # ガチホコの確保状況と位置
    rain_ctrl, loc_ratio = ikaRainmaker.getLocation(frame)  
    
    # カウント
    count = ikaRainmaker.getCount(frame)
    
    # 出力リストに記録
    return_list = rain_ctrl + count + loc_ratio
    
    
    return return_list



def processClam(frame):
    ''' ガチアサリのフレーム処理 '''
    # ゴール状況
    clam_ctrl = ikaClam.getControlTeam(frame)
    
    # カウント
    count = ikaClam.getCount(frame, clam_ctrl)
    
    # ペナルティカウント
    pena_list, pcount_list = ikaClam.getPenaltyCount(frame)
    
    # アサリの数
    clam_count = ikaClam.getClamNumber(frame)  
  
    # 出力リストに記録
    return_list =  [clam_ctrl] + count + pena_list + pcount_list + clam_count
    
    
    return return_list



def processColor(frame):
    ''' 塗り状況の把握 '''
    # ゴール状況
    clam_ctrl = ikaClam.getControlTeam(frame)
    
    # カウント
    count = ikaClam.getCount(frame, clam_ctrl)
    
    # ペナルティカウント
    pena_list, pcount_list = ikaClam.getPenaltyCount(frame)
    
    # アサリの数
    clam_count = ikaClam.getClamNumber(frame)  
  
    # 出力リストに記録
    return_list =  [clam_ctrl] + count + pena_list + pcount_list + clam_count
    
    
    return return_list



def work(video_path):
    ''' 動画処理 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path) 

    status_path = video_dir + '\\' + video_name + '_status.csv'
    
    if not (os.path.exists(status_path)):
        print('動画情報ファイルが見つかりません。先にikaMatchStatus.pyを実行してください。')
        
    else:    
        # 動画の情報を読み込む
        status_list = csvread.csvread(status_path, 's')
        rule        = status_list[1][0]
        stage_num   = int(status_list[1][1])
        zones_num   = int(status_list[1][2])
        fps         = float(status_list[1][3])
        frame_all   = int(status_list[1][4])
        frame_start = int(status_list[1][5])
        frame_end   = int(status_list[1][6])
        
        frame_end = frame_start + 30
    

        # イカランプ記録用のリスト
        lamp_path = video_dir + '\\' + video_name + '_lamp_test.csv'
        
        list_top = ['fcount']
        for i in range(len(player_list)):
            list_top += ['doa_' + str(player_list[i])]
            
        lamp_list = [list_top]
            
        
        # カウント記録用のリスト
        count_path = video_dir + '\\' + video_name + '_count_test.csv'
        
        list_top = ['fcount'] 
        if rule == 'turf':
            # 将来的に塗り状況を記録したい
            list_top += ['ratio_y', 'ratio_b']
        
        elif rule == 'zones':
            list_top += ['zones_ctrl', 'count_y', 'count_b', 'pena_y', 'pena_b', 'pena_count_y', 'pena_count_b']
            for i in range(zones_num):
                list_top = list_top + ['ratio_' + str(i+1) + '_y', 'ratio_' + str(i+1) + '_b']         
        
        elif rule == 'tower':
            list_top += ['tower_ctrl', 'count_y', 'count_b', 'loc_tower']

        elif rule == 'rain':
            list_top += ['rain_ctrl', 'count_y', 'count_b', 'loc_rain']   
            
        elif rule == 'clam':
            list_top += ['clam_ctrl', 'count_y', 'count_b', 
                         'pena_y', 'pena_b', 'pena_count_y', 'pena_count_b', 
                         'clam_num_y', 'clam_num_b']
            
        count_list = [list_top]


        # 動画処理はここから
        video = cv2.VideoCapture(video_path)
        W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        
        fcount = 0
        while(video.isOpened()):
            ret, frame = video.read()
        
            if not ret:
                break
          
            fcount += 1  
                
            if frame_start <= fcount < frame_end:
                if (fcount- frame_start) % frame_skip == 0:              
                    # フレームに対しての処理
                    # イカランプの状態取得
                    lamp_frame = processLamp(frame)
                    lamp_list.append([fcount] + lamp_frame)
                    
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
            
        
        print('完了')
        
        

def main():
    ''' メイン処理 '''
    for i in range(2, 3):
        # ビデオディレクトリ取得 '*'はワイルドカード
        fnames = glob.glob('.\\DAY' + str(i) + '\\PL-DAY' + str(i) + '_1*.avi' )
        
        for video_path in fnames:            
            video_name, video_ext = os.path.splitext(os.path.basename(video_path))
            
            print('=========================')
            print(video_name)
            
            work(video_path)
   
          

            
    
        
if __name__ == "__main__":
    main()