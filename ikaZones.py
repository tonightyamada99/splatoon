# -*- coding: utf-8 -*-

import cv2
import numpy as np

                
# 要素の位置の座標（画面サイズに可変で対応するために比率で設定）
# カウント表示
TL_count_ratio = [(804/1920, 154/1080), (1026/1920, 154/1080)]
BR_count_ratio = [(894/1920, 208/1080), (1116/1920, 208/1080)]
# ペナルティカウント表示 プラスの位置, 数字の位置
TL_pena_ratio = [(836/1920, 226/1080), (1010/1920, 226/1080), (862/1920, 220/1080), (1037/1920, 220/1080)]
BR_pena_ratio = [(874/1920, 254/1080), (1048/1920, 254/1080), (905/1920, 260/1080), (1080/1920, 260/1080)]
# エリア塗り状況
TL_zones_ratio = [( 916/1920, 158/1080), ( 916/1920, 144/1080), ( 916/1920, 197/1080)]
BR_zones_ratio = [(1004/1920, 194/1080), (1004/1920, 174/1080), (1004/1920, 227/1080)]



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
# mixとminとmaxで可読性最悪とか言わない
hsv_mix_min = [hsv_yel_min, hsv_blu_min, hsv_blk_min]
hsv_mix_max = [hsv_yel_max, hsv_blu_max, hsv_blk_max]

# RGBの閾値
# 白
rgb_wht_min = (128, 128, 128)
rgb_wht_max = (255, 255, 255)



# その他の閾値 threshold
# カウント表示の面積の一致率の閾値
thd_srf = 2000
# 数字の一致率の閾値
thd_val = 0.8
# 数字の幅
width_num_count = 10

# プラスの大きさの範囲
thd_plus = [19, 23]     # FHD(1920, 1080)


# 数字画像用 アルファチーム・ブラボーチーム
ab_list = ['alfa', 'bravo']



def getControlTeam(frame):
    ''' エリアの確保状況を判別 '''
    H, W = frame.shape[:2]
    
    # エリアの確保状況 in control -> 0:neutral 1:yellow 2:blue
    zones_ctrl = 0
    for i in range(2):
        # イエロー・ブルーのカウント表示切り取り
        TL_count = (round(W * TL_count_ratio[i][0]), round(H * TL_count_ratio[i][1]))
        BR_count = (round(W * BR_count_ratio[i][0]), round(H * BR_count_ratio[i][1]))
        
        img_trm = frame[TL_count[1] : BR_count[1], TL_count[0] : BR_count[0]]
        
        # RGB -> BGR -> HSV
        img_bgr = cv2.cvtColor(img_trm, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        bin_trm = cv2.inRange(img_hsv, hsv_mix_min[i], hsv_mix_max[i])
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

        
          
def getCount(frame, zones_ctrl):
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
    count_list = [0, 0]
    for i in range(2):
        # イエロー・ブルーのカウント表示切り取り
        TL_count = (round(W * TL_count_ratio[i][0]), round(H * TL_count_ratio[i][1]))
        BR_count = (round(W * BR_count_ratio[i][0]), round(H * BR_count_ratio[i][1]))
        
        img_trm = frame[TL_count[1] : BR_count[1], TL_count[0] : BR_count[0]]
        
        # RGB -> BGR -> HSV
        img_bgr = cv2.cvtColor(img_trm, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # HSV閾値で二値化
        bin_trm = cv2.inRange(img_hsv, hsv_ctrl_min[i], hsv_ctrl_max[i])
        # 白黒反転
        inv_trm = cv2.bitwise_not(bin_trm)


        # カウント100の判定
        img_path = '.\\count_zones\\count_zones_' + ab_list[i] + '_100.png'  
        img_num = cv2.imread(img_path)    
        
        img_bgr = cv2.cvtColor(img_num, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        bin_num = cv2.inRange(img_hsv, hsv_wht_min, hsv_wht_max)
        inv_num = cv2.bitwise_not(bin_num)
        
        # テンプレートマッチングで物体検出
        jug = cv2.matchTemplate(inv_trm, inv_num, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
        
        if maxVal > thd_val:
            # カウントは100で確定
            count_list[i] = 100
         
        else:   
            # カウントが100以下の時
            # 0~9の数字を読み込んで比較する
            num_list = []
            x_list = []
            for num in range(10):
                # 数字画像の読み込み
                img_path = '.\\count_zones\\count_zones_' + ab_list[i] + '_' + str(num) + '.png'  
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
                sort = np.argsort(-1 * val_all)
                
                # 最も一致度が高い場所
                idx_1st = sort[0]
                val_1st = val_all[idx_1st]
                
                # 一致率が閾値より大きい場合は数字と場所を記録
                # 同じ数字は最高でも２回しか出てこない
                if val_1st > thd_val:         
                    y_1st, x_1st = np.unravel_index(idx_1st, jug.shape)
                    num_list.append(num)
                    x_list.append(x_1st)
         
            
                    for j in range(1, len(sort)):
                        
                        if len(num_list) >= 2:
                            break
                        
                        # n番目に一致度が高い場所
                        idx_2nd = sort[j]
                        val_2nd = val_all[idx_2nd]
                        
                        # 一致率が閾値より大きい場合「かつ」１番目と場所が近くない場合は数字と場所を記録
                        if val_2nd > thd_val:       
                            y_2nd, x_2nd = np.unravel_index(idx_2nd, jug.shape)
                            
                            if abs(x_1st - x_2nd) > width_num_count:
                                num_list.append(num)
                                x_list.append(x_2nd)
                        else:
                            break

                            
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



def getPenaltyCount(frame):
    ''' ペナルティカウント取得 '''
    H, W = frame.shape[:2]

    # ペナルティカウントの有無の判別
    pena_list = [0, 0]
    scale_list = [0, 0]
    for i in [0, 1]:
        # プラス表示位置の切り取り
        TL = (round(W * TL_pena_ratio[i][0]), round(H * TL_pena_ratio[i][1]))
        BR = (round(W * BR_pena_ratio[i][0]), round(H * BR_pena_ratio[i][1]))
        img_trm = frame[TL[1]:BR[1], TL[0]:BR[0]]
        
        # RGB閾値で白黒に変換
        bin_trm = cv2.inRange(img_trm, rgb_wht_min, rgb_wht_max)
        # 白部分の大きさを計測
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_trm)
        
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        
        # プラス部分の最小時からの倍率を記録
        scale_tmp = [1]
        for index in range(num_labels):
            width  = stats[index][2]
            height = stats[index][3]
            
            # FHDでのサイズに変換
            width_conv = width / W * 1920
            height_conv = height / H * 1080
                              
            # プラス大きさが範囲内であれば倍率を記録
            if thd_plus[0] <= width_conv <= thd_plus[1]:
                scale_tmp.append(thd_plus[0] / width_conv)
                
            if thd_plus[0] <= height_conv <= thd_plus[1]:
                scale_tmp.append(thd_plus[0] / height_conv)
            
        # 記録した倍率で縮小してプラス画像と比較する
        val_list = []
        for scale in scale_tmp:          
            rsz_trm = cv2.resize(bin_trm, None, fx=scale, fy=scale)     
        
            # プラスの判定
            img_path = '.\\count_zones\\pena_zones_plus.png'  
            img_pls = cv2.imread(img_path)    
            
            bin_pls = cv2.inRange(img_pls, rgb_wht_min, rgb_wht_max)
            
            # テンプレートマッチングで物体検出
            jug = cv2.matchTemplate(rsz_trm, bin_pls, cv2.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
            
            if maxVal > thd_val:                     
                val_list.append(maxVal)
                pena_list[i] = 1
                
                
        if len(val_list) > 0:
            # プラスの一致率が最も大きい倍率を探す
            val_array = np.array(val_list)
            sort = np.argsort(-1 * val_array)
    
            scale_list[i] = scale_tmp[sort[0]] 
            
        
    count_list = [0, 0]
    # ここから数字の認識
    for i in [0, 1]:
        if pena_list[i] == 1:           
            # ペナルティカウント表示位置の切り取り
            TL = (round(W * TL_pena_ratio[i+2][0]), round(H * TL_pena_ratio[i+2][1]))
            BR = (round(W * BR_pena_ratio[i+2][0]), round(H * BR_pena_ratio[i+2][1]))
            img_trm = frame[TL[1]:BR[1], TL[0]:BR[0]] 

            # RGB閾値で白黒に変換
            bin_trm = cv2.inRange(img_trm, rgb_wht_min, rgb_wht_max)
            
            scale = scale_list[i]
            rsz_trm = cv2.resize(bin_trm, None, fx=scale, fy=scale)   
            
            num_list = []
            x_list = []
            for num in range(10):
                # 数字画像の読み込み
                img_path = '.\\count_zones\\pena_zones_' + str(num) + '.png'  
                img_num = cv2.imread(img_path)     
                
                bin_num = cv2.inRange(img_num, rgb_wht_min, rgb_wht_max)
                
                # テンプレートマッチングで物体検出
                jug = cv2.matchTemplate(rsz_trm, bin_num, cv2.TM_CCOEFF_NORMED)
                
                # 一致率をリスト化（正直この処理のメカニズムはよく分らん）
                val_all = np.reshape(jug, jug.shape[0]*jug.shape[1])
                # 一致率が高い順のインデックスを取得
                sort = np.argsort(-1 * val_all)
                
                # 最も一致度が高い場所
                idx_1st = sort[0]
                val_1st = val_all[idx_1st]
                
                # 一致率が閾値より大きい場合は数字と場所を記録
                # 同じ数字は最高でも２回しか出てこない
                if val_1st > thd_val:         
                    y_1st, x_1st = np.unravel_index(idx_1st, jug.shape)
                    num_list.append(num)
                    x_list.append(x_1st)
         
            
                    for j in range(1, len(sort)):
                        
                        if len(num_list) >= 2:
                            break
                        
                        # n番目に一致度が高い場所
                        idx_2nd = sort[j]
                        val_2nd = val_all[idx_2nd]
                        
                        # 一致率が閾値より大きい場合「かつ」１番目と場所が近くない場合は数字と場所を記録
                        if val_2nd > thd_val:       
                            y_2nd, x_2nd = np.unravel_index(idx_2nd, jug.shape)
                            
                            if abs(x_1st - x_2nd) > width_num_count:
                                num_list.append(num)
                                x_list.append(x_2nd)
                        else:
                            break

                            
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


    return pena_list, count_list



def getRatio(frame, zones_num):
    ''' エリアの塗り割合を認識 '''
    H, W = frame.shape[:2]
    
    # 記録用配列
    zones_ratio=[]
    
    # エリアが1個
    if zones_num == 1:
        idx_list = [0]
    # エリアが2個
    elif zones_num == 2:
        idx_list = [1, 2]
    else:
        idx_list = []   

        
    for i in idx_list:
        # エリア塗り状況表示の切り取り
        TL_zones = (round(W * TL_zones_ratio[i][0]), round(H * TL_zones_ratio[i][1]))
        BR_zones = (round(W * BR_zones_ratio[i][0]), round(H * BR_zones_ratio[i][1]))
        
        img_trm = frame[TL_zones[1] : BR_zones[1], TL_zones[0] : BR_zones[0]]
       
        # 色ごとに面積を計算 0:yellow 1:blue 2:black
        surf_list = [0, 0, 0]
        for color in range(3):
            # RGB -> BGR -> HSV
            img_bgr = cv2.cvtColor(img_trm, cv2.COLOR_RGB2BGR)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            bin_trm = cv2.inRange(img_hsv, hsv_mix_min[color], hsv_mix_max[color])
            # それぞれの色で二値化
            num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_trm)
            
            # 最大のラベルは画面全体を覆う黒なので不要．データを削除
            num_labels = num_labels - 1
            stats = np.delete(stats, 0, 0)
            center = np.delete(center, 0, 0)

            for index in range(num_labels):            
                s = stats[index][4]
                surf_list[color] += s
                
        surf_sum = surf_list[0] + surf_list[1] + surf_list[2]
        
        if surf_sum != 0:
            ratio_yel = surf_list[0] / surf_sum
            ratio_blu = surf_list[1] / surf_sum
            # 割合を記録
            zones_ratio.append(ratio_yel)
            zones_ratio.append(ratio_blu)
        else:
            # 0で割ってはいけない
            zones_ratio.append(0)
            zones_ratio.append(0)
 

    return zones_ratio



def correctCountList(count_list):
    ''' カウントを補正 '''
    # カウントは前のフレームと変わらないか1減るかのどちらか
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
    # for i in range(31, 32):
        
    #     img_path = '.\\sample_images\\sample_zones_' + str(i) + '.png'
    #     frame = cv2.imread(img_path) 
        
    #     print('====================================')
    #     print(img_path)        
    #     pena_count = getPenaltyCount(frame)
        
    #     print(pena_count)

        # zones_ctrl = getControlTeam(frame)
        # count_list = getCount(frame, zones_ctrl)
    
        # print(count_list) 
        
        # zones_num = 1            
        # zones_ratio = zonesRatio(frame, zones_num)
        # print(zones_ratio)
    
        # cv2.imshow('Preview', frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()    
    

        
if __name__ == "__main__":
    main()
    