# -*- coding: utf-8 -*-

import cv2
import csv
import os
import os.path
import numpy as np



TL_time_ratio = (0.475, 0.05)      # at FHD ( 912, 54)
BR_time_ratio = (0.525, 0.091666)  # at FHD (1008, 99)                   

TL_count_ratio = [(804/1920, 154/1080), (1026/1920, 154/1080)]  # at FHD 1920*1080
BR_count_ratio = [(894/1920, 208/1080), (1116/1920, 208/1080)]


# HSVの閾値
# 黄
hsv_yel_min = (90, 0, 128)
hsv_yel_max = (100, 255, 255)
# 青
hsv_blu_min = (165, 0, 128)
hsv_blu_max = (175, 255, 255)
# 白
hsv_wht_min = (0, 0, 0)
hsv_wht_max = (179, 128, 255)
# 黄と青と白
hsv_all_min = [hsv_yel_min, hsv_blu_min, hsv_wht_min]
hsv_all_max = [hsv_yel_max, hsv_blu_max, hsv_wht_max]

# カウント表示の面積の一致率の閾値
thd_srf = 2000

# 数字の一致率の閾値
thd_val = 0.8
# 数字の大きさ
width_num_count = 10

# 数字画像用 アルファチーム・ブラボーチーム
ab_list = ['alfa', 'blavo']



def zonesControl(frame):
    ''' エリアの確保状況を判別 '''
    H, W = frame.shape[:2]
    
    # エリアの確保状況 under control -> 0:neutral 1:yellow 2:blue
    zones_ctrl = 0
    for i in range(2):
        # イエロー・ブルーのカウント表示切り取り
        TL_count = (round(W * TL_count_ratio[i][0]), round(H * TL_count_ratio[i][1]))
        BR_count = (round(W * BR_count_ratio[i][0]), round(H * BR_count_ratio[i][1]))
        
        img_trimmed = frame[TL_count[1] : BR_count[1], TL_count[0] : BR_count[0]]
        
        # RGB -> BGR -> HSV
        img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        bin_trm = cv2.inRange(img_hsv, hsv_all_min[i], hsv_all_max[i])
        # それぞれの色で二値化
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_trm)
        
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)
        
        # イエロー・ブルーの総面積を計算
        sum_surf = 0  
        for index in range(num_labels):
            s = stats[index][4]
            sum_surf += s
            
        # 総面積が閾値以上 -> エリア確保中
        if sum_surf > thd_srf:
            zones_ctrl = i+1  
            
    
    return zones_ctrl
        
          
def zonesCount(frame, zones_ctrl):
    ''' ガチエリアのカウント取得 '''
    H, W = frame.shape[:2]
    
    # 確保状況に応じてHSV閾値を設定
    hsv_ctrl_min = [hsv_yel_min, hsv_blu_min]
    hsv_ctrl_max = [hsv_yel_max, hsv_blu_max]
    if zones_ctrl == 1:
        hsv_ctrl_min[0] = hsv_wht_min
        hsv_ctrl_max[0] = hsv_wht_max        
    elif zones_ctrl == 2:
        hsv_ctrl_min[1] = hsv_wht_min
        hsv_ctrl_max[1] = hsv_wht_max  
        
        
    # ここからカウント数字の認識
    count_list = []
    for i in range(2):
        # イエロー・ブルーのカウント表示切り取り
        TL_count = (round(W * TL_count_ratio[i][0]), round(H * TL_count_ratio[i][1]))
        BR_count = (round(W * BR_count_ratio[i][0]), round(H * BR_count_ratio[i][1]))
        
        img_trimmed = frame[TL_count[1] : BR_count[1], TL_count[0] : BR_count[0]]
        
        # RGB -> BGR -> HSV
        img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # HSV閾値で二値化
        bin_trm = cv2.inRange(img_hsv, hsv_ctrl_min[i], hsv_ctrl_max[i])
        # 白黒反転
        inv_trm = cv2.bitwise_not(bin_trm)
        
        # 0~9の数字を読み込んで比較する
        num_list = []
        x_list = []
        for num in range(10):
            # 数字画像の読み込み
            img_path = '.\count_zones\\count_zones_' + ab_list[i] + '_' + str(num) + '.png'  
            img_num = cv2.imread(img_path)     
            
            img_bgr = cv2.cvtColor(img_num, cv2.COLOR_RGB2BGR)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            bin_num = cv2.inRange(img_hsv, hsv_wht_min, hsv_wht_max)
            inv_num = cv2.bitwise_not(bin_num)
            
            # テンプレートマッチングで物体検出
            jug = cv2.matchTemplate(inv_trm, inv_num, cv2.TM_CCOEFF_NORMED)
            
            # 一致率をリスト化（正直この処理のメカニズムはよく分らん）
            val_all = np.reshape(jug, jug.shape[0]*jug.shape[1])
            # 一致率が高い順のインデックスを取得
            sort = np.argsort(-val_all)
            
            # 最も一致度が高い場所
            idx_1st = sort[0]
            val_1st = val_all[idx_1st]
            
            # 一致率が閾値より大きい場合は数字と場所を記録
            # 同じ数字は最高でも２回しか出てこない
            if val_1st > thd_val:         
                y_1st, x_1st = np.unravel_index(idx_1st, jug.shape)
                num_list.append(num)
                x_list.append(x_1st)
     
                # ２番目に一致度が高い場所
                idx_2nd = sort[1]
                val_2nd = val_all[idx_2nd]
                
                # 一致率が閾値より大きい場合「かつ」１番目と場所が近くない場合は数字と場所を記録
                if val_2nd > thd_val:        
                    y_2nd, x_2nd = np.unravel_index(idx_2nd, jug.shape)
                    
                    if abs(x_1st - x_2nd) > width_num_count:
                        num_list.append(num)
                        x_list.append(x_2nd)
                        
        # 座標が大きい順のインデックスを取得
        pt_list = np.array(x_list)
        sort = np.argsort(-pt_list)
        # 各桁の数字
        dig_list = [0, 0, 0]
        for i in range(len(sort)):
            # 数字置き換え
            dig_list[2-i] = num_list[sort[i]]
        
        # カウント数字を計算
        count = dig_list[0] * 100 + dig_list[1] * 10 + dig_list[2]
        count_list.append(count)
     
    
    return count_list


    
def main():
    ''' メイン処理 ''' 
    # img_path = 'img_count_20.png'
    # frame = cv2.imread(img_path) 
    
    # zones_ctrl = zonesControl(frame)
    # count_list = zonesCount(frame, zones_ctrl)
    
    # print(count_list)


    match = 'PL-DAY2_3-3'
    
    frame_start = 910
    frame_end = 14087
    
    # 何フレームごとに処理を行うか
    frame_skip = 1
    
    video_path = 'D:\splatoon_movie\PremiereLeague\DAY2\\' + match + '.avi'
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    csv_path = video_name + '_count_test.csv'


    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # 以下フレーム処理結果の準備
    # 記録用のリスト
    count_list = [['fcount', 'y_count', 'b_count']]

    
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
                zones_ctrl = zonesControl(frame)
                count = zonesCount(frame, zones_ctrl)
          
                count_list.append([fcount] +  count)
                
        if fcount == frame_end:
            break
                
    video.release

    # CSV出力
    with open(csv_path, 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(count_list)
         
    
    
    
        
if __name__ == "__main__":
    main()
    