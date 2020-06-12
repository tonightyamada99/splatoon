# -*- coding: utf-8 -*-

import cv2
import csv
import os.path
import numpy as np

# TopLeft, BottomRight
TLBR_y = [(480, 40), (920, 100)] 
TLBR_b = [(1000, 40), (1440, 100)]

TLBR_list = [TLBR_y, TLBR_b]

TLBR_y_danger = [(420, 27), (600, 108)]     # at FHD (912, 54)
TLBR_b_danger = [(1320, 27), (1500, 108)]    # at FHD (912, 81)

TLBR_list_danger = [TLBR_y_danger, TLBR_b_danger]

# HSVの閾値
hsv_y_min = (90, 128, 128)
hsv_y_max = (100, 255, 255)

hsv_b_min = (165, 128, 128)
hsv_b_max = (175, 255, 255)

hsv_sp_min = (0, 0, 128)
hsv_sp_max = (179, 128, 255)

hsv_d_min = (70, 0, 192)
hsv_d_max = (90, 255, 255)

hsv_a_min = [hsv_y_min, hsv_b_min]
hsv_a_max = [hsv_y_max, hsv_b_max]


# 各プレイヤーのイカランプの位置
# ピンチ表示に対して調整が必要
TL_lamp_n = [(518, 47), (629, 47), (709, 47), (792, 47), (1047, 47), (1130, 47), (1220, 47), (1311, 47)] 
BR_lamp_n = [(608, 92), (699, 92), (789, 92), (872, 92), (1127, 92), (1210, 92), (1290, 92), (1401, 92)]

TL_lamp_y = [(570, 50), (646, 50), (721, 50), (797, 50), (1042, 42), (1138, 42), (1236, 42), (1332, 42)]
BR_lamp_y = [(642, 90), (718, 90), (793, 90), (869, 90), (1130, 96), (1226, 96), (1324, 96), (1420, 96)]

TL_lamp_b = [(498, 42), (596, 42), (692, 42), (789, 42), (1049, 50), (1125, 50), (1200, 50), (1276, 50)] 
BR_lamp_b = [(586, 96), (684, 96), (780, 96), (877, 96), (1121, 90), (1197, 90), (1272, 90), (1348, 90)]

    
def jugLamp(video_path):
    ''' イカランプの判別 '''      
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    video = cv2.VideoCapture(video_path)
    print(video.isOpened())
    
    
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    doa_list = [] # Dead or Alive

    fcount = 0
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount += 1  
    
            
        if fcount % 30 == 0:
            
            print(fcount)
            
            #イカランプの大きさ 0:normal  1:danger yellow  2:danger blue
            danger_num = 0 
            
            for i in (0, 1):
                TL_danger = TLBR_list_danger[i][0]
                BR_danger = TLBR_list_danger[i][1]
                img_trimmed = frame[TL_danger[1] : BR_danger[1], TL_danger[0] : BR_danger[0]] 
                
                img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
                img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
                      
                img_bin = cv2.inRange(img_hsv, hsv_d_min, hsv_d_max)
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                       
                for index in range(num_labels):
                    s = stats[index][4]
                                 
                    if s > 1000:
                        danger_num = i + 1 
                        
    
            # イカランプの状態リスト 0:dead  1:alive  2:sp
            lamp_list = [0, 0, 0, 0, 0, 0, 0, 0]
            # 面積を記録しておく
            surf_list = [0, 0, 0, 0, 0, 0, 0, 0]
            
            if danger_num == 0:
                TL_lamp = TL_lamp_n
                BR_lamp = BR_lamp_n

            elif danger_num == 1:
                TL_lamp = TL_lamp_y
                BR_lamp = BR_lamp_y
                
            elif danger_num == 2:
                TL_lamp = TL_lamp_b
                BR_lamp = BR_lamp_b   
                
                
            for i in (0, 1):
                # イカランプ部分をトリミング
                TL = TLBR_list[i][0]
                BR = TLBR_list[i][1]
                img_trimmed = frame[TL[1] : BR[1], TL[0] : BR[0]] 
                
                img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
                img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
                      
                # alive の判定
                img_bin = cv2.inRange(img_hsv, hsv_a_min[i], hsv_a_max[i])
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                       
                for index in range(num_labels):
                    s = stats[index][4]
                    mx = int(center[index][0]) + TL[0]
                    
                    for player_num in range(int(4*i), int(4*(i+1))):    
                        # まとまりがアイコン表示位置に入っているか             
                        if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                            # 面積が前より大きければ大きいほうを採用
                            if surf_list[player_num] < s:                     
                                lamp_list[player_num] = 1
                                surf_list[player_num] = s
                            
                # sp の判定
                img_bin = cv2.inRange(img_hsv, hsv_sp_min, hsv_sp_max)
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                    
                for index in range(num_labels):
                    s = stats[index][4]
                    mx = int(center[index][0]) + TL[0]
                    
                    for player_num in range(int(4*i), int(4*(i+1))):                        
                        if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                            if surf_list[player_num] < s:                     
                                lamp_list[player_num] = 2
                                surf_list[player_num] = s
                                
                                
            # 面積の閾値を設けて誤認識をdeadに戻す
            for player_num in range(8):
                if surf_list[player_num] < 800: # 閾値はFHD向けで調整が必要そう
                    lamp_list[player_num] = 0
        

            doa_list.append([fcount] + lamp_list)

                        
    video.release

    # CSV出力
    with open(video_name + '_lamp.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(doa_list)



def jugLampImg(img_path): 
    ''' 画像でイカランプ判別の練習 '''
    # イカランプの状態リスト 0:dead  1:alive  2:sp
    lamp_list = [0, 0, 0, 0, 0, 0, 0, 0]
    # 面積を記録しておく
    surf_list = [0, 0, 0, 0, 0, 0, 0, 0]

    frame = cv2.imread(img_path)        
    
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
            
            for player_num in range(int(4*i), int(4*(i+1))):    
                # まとまりがアイコン表示位置に入っているか             
                if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                    # 面積が前より大きければ大きいほうを採用
                    if surf_list[player_num] < s:                     
                        lamp_list[player_num] = 1
                        surf_list[player_num] = s
                    
        # sp の判定
        img_bin = cv2.inRange(img_hsv, hsv_sp_min, hsv_sp_max)
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
    
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)
            
        for index in range(num_labels):
            s = stats[index][4]
            mx = int(center[index][0]) + TL[0]
            
            for player_num in range(int(4*i), int(4*(i+1))):                        
                if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                    if surf_list[player_num] < s:                     
                        lamp_list[player_num] = 2
                        surf_list[player_num] = s
                        
        # 面積の閾値を設けて誤認識をdeadに戻す
        for player_num in range(8):
            if surf_list[player_num] < 1000: # 閾値はFHD向けで調整が必要そう
                lamp_list[player_num] = 0
                
        
        print(lamp_list)
        print(surf_list)
                    
    
def main():
    ''' メイン処理 '''
      
    video_path = 'F:\splatoon_movie\PremiereLeague\\capture (20200610-2242).avi'
    jugLamp(video_path)
    
    
        
if __name__ == "__main__":
    main()