# -*- coding: utf-8 -*-

import cv2
import csv
import os.path

import ikaColor

# 対象動画情報(MatchStatus等から取得)
match = 'PL-DAY1_1-1'
frame_start = 400
frame_end = 6200

# 何フレームごとに処理を行うか
frame_skip = 30

#あとみーのディレクトリ
video_path = 'C:\\Users\\nfkat\\Documents\\splatoon\\PremiereLeague\\' + match + '.mp4'
#video_path = 'D:\splatoon_movie\PremiereLeague\DAY2\\' + match + '.avi'
video_name, video_ext = os.path.splitext(os.path.basename(video_path))

csv_path = video_name + '_turf_color.csv'


def getColorRatioTurf():
    ''' 動画処理 '''
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # 以下フレーム処理結果の準備
    # 記録用のリスト
    list_top = []

    # 色ピクセル数
    list_top.append('yellow_count')
    list_top.append('blue_count')

    # 各フレームでの黄色と青の合計ピクセル数
    list_top.append('sum_count')

    # 各フレームでの塗り残しを考慮しない色割合
    list_top.append('yellow_ratio1')
    list_top.append('bule_ratio1')

    # 各フレームでの塗り残しを考慮した色割合
    list_top.append('yellow_ratio2')
    list_top.append('blue_ratio2')
    list_top.append('other_ratio')
     
    record = [list_top]

    max_color_count = 0
           
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
               
                # 記録用のリスト
                record_frame = []
                
                color = ikaColor.getColorRatioNawabari(frame)
                record_frame.append(color[0])
                record_frame.append(color[1])
                record_frame.append(color[0] + color[1])
                record_frame.append(color[0] /(color[0] + color[1] + 1) * 100)
                record_frame.append(100 - record_frame[3])
                
                record.append(record_frame)

                if(fcount <= frame_end -1):
                    max_color_count = record_frame[2]
  
        if fcount == frame_end:
           break
               
    video.release

    print(max_color_count) 
   
    for i in range(len(record)):
        if(i > 0):
            record[i].append(record[i][0] / max_color_count * 100)
            record[i].append(record[i][1] / max_color_count * 100)
            record[i].append(100 - record[i][5] - record[i][6])
    

    # CSV出力
    with open(csv_path, 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(record)

def main():
    ''' メイン処理 '''
    getColorRatioTurf()
    
        
if __name__ == "__main__":
    main()