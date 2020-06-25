# -*- coding: utf-8 -*-

import cv2
import numpy as np



# ピンチの位置
# イエローチーム
TLBR_y_danger = [(420, 27), (600, 108)]    # TopLeft, BottomRight
# ブルーチーム
TLBR_b_danger = [(1320, 27), (1500, 108)]
# イエローとブルーをまとめる
TLBR_list_danger = [TLBR_y_danger, TLBR_b_danger]


# 各プレイヤーのイカランプの位置
# 通常～微優劣
TL_lamp_n = [(518, 47), (629, 47), (709, 47), (792, 47), (1047, 47), (1130, 47), (1220, 47), (1311, 47)] 
BR_lamp_n = [(608, 92), (699, 92), (789, 92), (872, 92), (1127, 92), (1210, 92), (1290, 92), (1401, 92)]
# イエローがピンチ
TL_lamp_y = [(570, 50), (646, 50), (721, 50), (797, 50), (1042, 42), (1138, 42), (1236, 42), (1332, 42)]
BR_lamp_y = [(642, 90), (718, 90), (793, 90), (869, 90), (1130, 96), (1226, 96), (1324, 96), (1420, 96)]
# ブルーがピンチ
TL_lamp_b = [(498, 42), (596, 42), (692, 42), (789, 42), (1049, 50), (1125, 50), (1200, 50), (1276, 50)] 
BR_lamp_b = [(586, 96), (684, 96), (780, 96), (877, 96), (1121, 90), (1197, 90), (1272, 90), (1348, 90)]


# HSVの閾値(0~179, 0~255, 0~255)
# ピンチ！
hsv_p_min = (70, 0, 192)
hsv_p_max = (90, 255, 255)
# イエローチーム
hsv_y_min = (90, 128, 128)
hsv_y_max = (100, 255, 255)
# ブルーチーム
hsv_b_min = (165, 128, 128)
hsv_b_max = (175, 255, 255)
# スペシャル状態
hsv_sp_min = (0, 16, 128)
hsv_sp_max = (179, 128, 255)
# やられた状態
hsv_d_min = (0, 0, 0)
hsv_d_max = (255, 16, 255)


    
def judgeDanger(frame):
    ''' ピンチの判別 '''            
    # ピンチ！は英語版だとDnager!らしい     
    # イカランプの大きさ 0:normal  1:danger yellow  2:danger blue
    danger_num = 0
    
    for i in (0, 1):
        
        TL_danger = TLBR_list_danger[i][0]
        BR_danger = TLBR_list_danger[i][1]
        img_trimmed = frame[TL_danger[1] : BR_danger[1], TL_danger[0] : BR_danger[0]] 
        
        img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
              
        img_bin = cv2.inRange(img_hsv, hsv_p_min, hsv_p_max)
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
        
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)
               
        for index in range(num_labels):
            s = stats[index][4]
                           
            if s > 1000:
                danger_num = i + 1 
                
    return danger_num


def judgeLamp(frame, danger_num, player_num):
    ''' イカランプの判別 '''
    # イカランプの状態を数字で記録 0:dead  1:alive  2:sp
    doa = 0     # Dead or Alive
    # それぞれの状態の面積を記録しておく
    surf_list = [0, 0, 0]
    
    if danger_num == 0:
        TL_lamp = TL_lamp_n
        BR_lamp = BR_lamp_n

    elif danger_num == 1:
        TL_lamp = TL_lamp_y
        BR_lamp = BR_lamp_y
        
    elif danger_num == 2:
        TL_lamp = TL_lamp_b
        BR_lamp = BR_lamp_b        
        
    
    # イカランプ部分をトリミング
    TL = TL_lamp[player_num-1]
    BR = BR_lamp[player_num-1]
    img_trimmed = frame[TL[1] : BR[1], TL[0] : BR[0]] 
    
    # BGR -> RGB -> HSV
    img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)  
    
    # dead の判定
    img_bin = cv2.inRange(img_hsv, hsv_d_min, hsv_d_max)
    num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
    
    num_labels = num_labels - 1
    stats = np.delete(stats, 0, 0)
    center = np.delete(center, 0, 0)
        
    for index in range(num_labels):
        s = stats[index][4]
        surf_list[0] += s
   
    # alive の判定
    if player_num <= 4:
        hsv_a_max = hsv_y_max
        hsv_a_min = hsv_y_min
    elif player_num >= 5:
        hsv_a_max = hsv_b_max
        hsv_a_min = hsv_b_min        
        
    img_bin = cv2.inRange(img_hsv, hsv_a_min, hsv_a_max)
    num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
    
    num_labels = num_labels - 1
    stats = np.delete(stats, 0, 0)
    center = np.delete(center, 0, 0)
           
    for index in range(num_labels):
        s = stats[index][4]
        surf_list[1] += s
        
    # sp の判定
    img_bin = cv2.inRange(img_hsv, hsv_sp_min, hsv_sp_max)
    num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)

    num_labels = num_labels - 1
    stats = np.delete(stats, 0, 0)
    center = np.delete(center, 0, 0)
        
    for index in range(num_labels):
        s = stats[index][4]
        surf_list[2] += s
        
    # 面積リストの値(総面積)が一番大きいインデックス -> イカランプの状態    
    doa = np.argmax(surf_list)

    return doa, surf_list

    
def main():
    ''' メイン処理 '''
    img_path = 'image_9.png'
    frame = cv2.imread(img_path)
    
    player_list = [i for i in range(1, 9)]
    
    danger_num = judgeDanger(frame)
    
    for player_num in player_list:
        doa, surf_list = judgeLamp(frame, danger_num, player_num)
        
        print(doa)
        print(surf_list)
    
        
if __name__ == "__main__":
    main()