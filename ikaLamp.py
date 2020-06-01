# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 04:18:05 2019

@author: Yamada
"""

import cv2
import csv
import glob
import os.path
import numpy as np
from PIL import Image

# TopLeft, BottomRight
TLBR_y = [(480, 40), (920, 100)] 
TLBR_b = [(1000, 40), (1440, 100)]

TLBR_list = [TLBR_y, TLBR_b]

# HSVの閾値
hsv_y_min = (90, 128, 128)
hsv_y_max = (100, 255, 255)

hsv_b_min = (165, 128, 128)
hsv_b_max = (175, 255, 255)

hsv_sp_min = (0, 0, 128  )
hsv_sp_max = (179, 128, 255)

# 各プレイヤーのイカランプの位置
TL_lamp = [(518, 47), (629, 47), (709, 47), (792, 47), (1047, 47), (1130, 47), (1220, 47), (1311, 47)] 
BR_lamp = [(608, 92), (699, 92), (789, 92), (872, 92), (1127, 92), (1210, 92), (1290, 92), (1401, 92)] 

    
def jugLamp(video_path, frame_start, frame_end):
    ''' イカランプの判別 '''      
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    doa_list = [] # Dead or Alive

    fcount = 0
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount = fcount + 1  
        
        if frame_start <= fcount < frame_end:
            # イカランプの状態リスト 0:dead  1:alive  2:sp
            lamp_list = [0, 0, 0, 0, 0, 0, 0, 0]
            
            for i in range(1):
                # イカランプ部分をトリミング
                TL = TLBR_list[i][0]
                BR = TLBR_list[i][1]
                img_trimmed = frame[TL[1] : BR[1], TL[0] : BR[0]] 
                
                img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
                img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
                      
                # alive の判定
                img_bin = cv2.inRange(img_hsv, hsv_y_min, hsv_y_max)
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                       
                for index in range(num_labels):
                    s = stats[index][4]
                    mx = int(center[index][0]) + TL[0]
                    
                    if s > 500:
                        for player_num in range(int(4*i), int(4*(i+1))):                        
                            if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                                lamp_list[player_num] = 1
                                
                # sp の判定
                img_bin = cv2.inRange(img_hsv, hsv_sp_min, hsv_sp_max)
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                    
                for index in range(num_labels):
                    s = stats[index][4]
                    mx = int(center[index][0]) + TL[0]
                    
                    if s > 500:
                        for player_num in range(int(4*i), int(4*(i+1))):                        
                            if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                                lamp_list[player_num] = 2
        
                    
            doa_list.append(lamp_list)
                
        elif fcount == frame_end:
            break
                                
    video.release

    # CSV出力
    with open(video_name + '_lamp.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(doa_list)

    
def main():
    ''' メイン処理 '''
      
    video_path = 'D:\\splatoon_movie\\capture\\overlook_turf\\overlook_turf_stage0.avi'
    frame_start = 484
    frame_end = 1000
    jugLamp(video_path, frame_start, frame_end)
    
    
        
if __name__ == "__main__":
    main()