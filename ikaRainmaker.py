# -*- coding: utf-8 -*-

import cv2
import numpy as np

                
# 要素の位置の座標（画面サイズに可変で対応するために比率で設定）
# 「のこり」の表示位置, 数字の表示位置
TL_count_ratio = [( 430/1920, 204/1080), ( 430/1920, 218/1080)]
BR_count_ratio = [(1490/1920, 218/1080), (1490/1920, 258/1080)]
# ガチホコ位置表示, ゲージの左右端の座標
TL_scale_ratio = [( 490/1920, 130/1080), ( 514/1920, 155/1080)]
BR_scale_ratio = [(1430/1920, 178/1080), (1405/1920, 155/1080)]


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
# 黒
hsv_blk_min = (0, 0, 0)
hsv_blk_max = (179, 128, 128)
# 黄と青と黒をまとめる
hsv_mix_min = [hsv_yel_min, hsv_blu_min, hsv_blk_min]
hsv_mix_max = [hsv_yel_max, hsv_blu_max, hsv_blk_max]


# その他の閾値 threshold
# テンプレートマッチングの一致率の閾値
thd_val = 0.85
# 数字の一致率の閾値
thd_num = 0.8

# カウント表示の幅
width_count = 60/1920
# 数字の幅
width_num_count = 5


# 数字画像用 アルファチーム・ブラボーチーム
ab_list = ['alfa', 'bravo']



def getLocation(frame):
    ''' ガチホコの位置と確保状況判別 '''
    H, W = frame.shape[:2]
    
    # 位置表示部分の切り取り
    TL_scale = (round(W * TL_scale_ratio[0][0]), round(H * TL_scale_ratio[0][1]))
    BR_scale = (round(W * BR_scale_ratio[0][0]), round(H * BR_scale_ratio[0][1]))
    img_trm = frame[TL_scale[1] : BR_scale[1], TL_scale[0] : BR_scale[0]]
    
    val_list = []
    loc_list = []
    
    for color in ['neu', 'yel', 'blu']:
        img_path = '.\\count_rainmaker\\rain_scale_' + color + '.png'
        img_tmp = cv2.imread(img_path) 
        
        # テンプレートマッチングで物体検出
        jug = cv2.matchTemplate(img_trm, img_tmp, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)
        
        # 円の中心のx座標を記録
        height, width = img_tmp.shape[:2]
        loc = int(TL_scale[0] + maxLoc[0] + width / 2)
        
        val_list.append(maxVal)
        loc_list.append(loc)
    
    # 一致率が大きい順のインデックスを取得
    val_list = np.array(val_list)
    sort = np.argsort(-1 * val_list)
            
    # ガチホコの確保状況 in control -> 0:neutral 1:yellow 2:blue
    rain_ctrl = sort[0] 
    # ガチホコの位置
    rain_loc  = loc_list[sort[0]]

    # ガチホコの位置は-1~1の範囲で記録
    # -1:ブルーのゴール（左端） 1:イエローのゴール（右端）
    scale_left  = round(W * TL_scale_ratio[1][0])
    scale_right = round(W * BR_scale_ratio[1][0])
    scale_center = (scale_left + scale_right) / 2
    loc_ratio = (rain_loc - scale_center) / (scale_right - scale_center)
    
    
    return rain_ctrl, loc_ratio
        
          
def getCount(frame):
    ''' カウント数字の取得 '''
    H, W = frame.shape[:2]
    
    # 「のこり」位置表示部分の切り取り
    TL_remain = (round(W * TL_count_ratio[0][0]), round(H * TL_count_ratio[0][1]))
    BR_remain = (round(W * BR_count_ratio[0][0]), round(H * BR_count_ratio[0][1]))
    img_trm = frame[TL_remain[1] : BR_remain[1], TL_remain[0] : BR_remain[0]]
    
    # 「のこり」表示を認識
    loc_list = [0, 0]
    
    for i, color in enumerate(['yel', 'blu']):
        img_path = '.\\count_rainmaker\\remaining_rain_' + color + '.png'
        img_tmp = cv2.imread(img_path) 
        
        # テンプレートマッチングで物体検出
        jug = cv2.matchTemplate(img_trm, img_tmp, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)
        
        # 「のこり」が表示されていないこともあるので一致率に閾値を設ける
        if maxVal > thd_val:            
            # 「のこり」の中心のx座標を記録
            height, width = img_tmp.shape[:2]
            loc = int(TL_remain[0] + maxLoc[0] + width / 2)

            loc_list[i] = loc

    # カウントを記録
    count_list = [100, 100]
    
    for i, loc in enumerate(loc_list):
        
        # 「のこり」の座標が記録されていない -> のこりカウントは100
        if loc == 0:
            continue
        
        # カウント表示切り取り
        x_left  = int(loc - width_count * W / 2)
        x_right = int(loc + width_count * W / 2)
        TL_count = (x_left , round(H * TL_count_ratio[1][1]))
        BR_count = (x_right, round(H * BR_count_ratio[1][1])) 
        
        img_trm = frame[TL_count[1] : BR_count[1], TL_count[0] : BR_count[0]]

        # RGB -> BGR -> HSV
        img_bgr = cv2.cvtColor(img_trm, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # HSV閾値で二値化
        bin_trm = cv2.inRange(img_hsv, hsv_wht_min, hsv_wht_max)
        # 白黒反転
        inv_trm = cv2.bitwise_not(bin_trm)
               
        # 0~9の数字を読み込んで比較する
        num_list = []
        x_list = []
        for num in range(10):
            # 数字画像の読み込み
            img_path = '.\\count_rainmaker\\count_rain_' + ab_list[i] + '_' + str(num) + '.png'  
            img_num = cv2.imread(img_path)     
            
            # 白黒画像に変換
            img_bgr = cv2.cvtColor(img_num, cv2.COLOR_RGB2BGR)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            bin_num = cv2.inRange(img_hsv, hsv_wht_min, hsv_wht_max)
            inv_num = cv2.bitwise_not(bin_num)

            # テンプレートマッチングで物体検出
            jug = cv2.matchTemplate(inv_trm, inv_num, cv2.TM_CCOEFF_NORMED)
            
            # 一致率をリスト化（正直この処理のメカニズムはよく分らん）
            val_all = np.reshape(jug, jug.shape[0]*jug.shape[1])
            # 一致率が高い順のインデックスを取得
            sort = np.argsort(-1 * val_all)
            
            # 最も一致度が高い場所
            idx_1st = sort[0]
            val_1st = val_all[idx_1st]
            
            # 一致率が閾値より大きい場合は数字と場所を記録
            # 同じ数字は最高でも２回しか出てこない
            if val_1st > thd_num:         
                y_1st, x_1st = np.unravel_index(idx_1st, jug.shape)
                num_list.append(num)
                x_list.append(x_1st)
     
                # ２番目に一致度が高い場所
                idx_2nd = sort[1]
                val_2nd = val_all[idx_2nd]
                
                # 一致率が閾値より大きい場合「かつ」１番目と場所が近くない場合は数字と場所を記録
                if val_2nd > thd_num:        
                    y_2nd, x_2nd = np.unravel_index(idx_2nd, jug.shape)
                    
                    if abs(x_1st - x_2nd) > width_num_count:
                        num_list.append(num)
                        x_list.append(x_2nd)
                        
        # 座標が大きい順のインデックスを取得
        pt_list = np.array(x_list)
        sort = np.argsort(-1 * pt_list)
        # 各桁の数字
        dig_list = [0, 0]
        for j in range(len(sort)):
            # 数字置き換え
            dig_list[1-j] = num_list[sort[j]]
        
        # カウント数字を計算
        count = dig_list[0] * 10 + dig_list[1]
        count_list[i] = count
     
    
    return count_list


def correctCount(count_list):
    
    cor_count_list = [100]
    count_pre = 100
    for i in range(1, len(count_list)):     
        count_now = count_list[i]
        dif = count_pre - count_now
        
        if dif == 0 or dif == 1:
            cor_count = count_now
        else:
            cor_count = count_pre
            
        cor_count_list.append(cor_count)
        
        count_pre = cor_count
        
    
    return cor_count_list


def main():
    ''' メイン処理 ''' 
    # for i in range(1, 14):
    #     img_path = '.\\sample_images\\sample_rain_' + str(i) + '.png'
    #     frame = cv2.imread(img_path) 
        
    #     print('====================================')
    #     print(img_path)
        
    #     # rain_ctrl, loc_ratio = getLocation(frame)
    #     # print(rain_ctrl)
    #     # print(rain_ratio)
        
    #     count_list = getCount(frame)
    #     print(count_list)
        
    #     cv2.imshow('', frame)
    #     cv2.waitKey()
    #     cv2.destroyAllWindows()
    


    
        
if __name__ == "__main__":
    main()
    