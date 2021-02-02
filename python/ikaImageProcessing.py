# -*- coding: utf-8 -*-

####################################
# スプラトゥーン用の画像処理まとめ #
# 作成者：こんやがやまだ           #
####################################

import cv2
import numpy as np


# 色閾値 threshold
# RGB[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), (128, 128, 128)],
           'wht':[(128, 128, 128), (255, 255, 255)]}

# HSV[min, max](0~179, 0~255, 0~255)
thd_hsv = {'blk':[(  0,   0,   0), (179,  64, 128)],    # 黒
           'wht':[(  0,   0, 128), (179,  64, 255)],    # 白
           'dng':[( 70,   0, 192), ( 90, 255, 255)],    # ピンチ danger
           'spw':[(  0,  16, 128), (179, 128, 255)],    # スペシャル状態 
           'yel':[( 90, 128, 128), (100, 255, 255)],
           'blu':[(165, 128, 128), (175, 255, 255)]}



def matchRGB(template, image, TL, BR, threshold):
    ''' 
    RGB版：対象画像の指定箇所を切り抜いて比較画像との一致率を算出する
    template    : 比較画像（二値画像）
    image       : 対象画像
    TL          : 切り取り左上座標
    BR          : 切り取り右下座標
    threshold   : 色閾値 [min, max] で指定  
    '''        
    # 対象の切り抜き
    l, t = TL
    r, b = BR
    img_trm = image[t:b, l:r]

    # 閾値を設定
    # リスト形式
    if type(threshold) is list:
        thd_min, thd_max = threshold
    # 色指定
    elif type(threshold) is str:
        thd_min, thd_max = thd_rgb[threshold]  
        
    # 閾値で2値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
        
    # 一致率の算出
    jug = cv2.matchTemplate(bin_trm, template, cv2.TM_CCORR_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
    

    return maxVal



def matchHSV(template, image, TL, BR, threshold):
    ''' 
    HSV版：対象画像の指定箇所を切り抜いて比較画像との一致率を算出する
    template    : 比較画像（二値画像）
    image       : 対象画像
    TL          : 切り取り左上座標
    BR          : 切り取り右下座標
    threshold   : 色閾値 [min, max] で指定  
    '''        
    # 対象の切り抜き
    l, t = TL
    r, b = BR
    img_trm = image[t:b, l:r]
    
    # RGB -> BGR -> HSV
    bgr_trm = cv2.cvtColor(img_trm, cv2.COLOR_RGB2BGR)
    hsv_trm = cv2.cvtColor(bgr_trm, cv2.COLOR_BGR2HSV)

    # 閾値の設定
    # リスト形式
    if type(threshold) is list:
        thd_min, thd_max = threshold
    # 色指定
    elif type(threshold) is str:
        thd_min, thd_max = thd_hsv[threshold]
        
    # 閾値で2値化
    bin_trm = cv2.inRange(hsv_trm, thd_min, thd_max)
        
    # 一致率の算出
    jug = cv2.matchTemplate(bin_trm, template, cv2.TM_CCORR_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)
    

    return maxVal



def matchMaskRGB(template, image, TL, BR, threshold):
    ''' 
    RGB版：対象画像の指定箇所を切り抜いてマスク処理した後で比較画像との一致率を算出する
    template    : 比較画像（二値画像）
    image       : 対象画像
    TL          : 切り取り左上座標
    BR          : 切り取り右下座標
    threshold   : 色閾値 [min, max] で指定  
    '''        
    # 対象の切り抜き
    l, t = TL
    r, b = BR
    img_trm = image[t:b, l:r]

    # 閾値を設定
    # リスト形式
    if type(threshold) is list:
        thd_min, thd_max = threshold
    # 色指定
    elif type(threshold) is str:
        thd_min, thd_max = thd_rgb[threshold]  
        
    # 閾値で2値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
    # マスク処理
    msk_trm = cv2.bitwise_and(bin_trm, template) 
        
    # 一致率の算出
    jug = cv2.matchTemplate(msk_trm, template, cv2.TM_CCORR_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
    

    return maxVal



def matchMaskHSV(template, image, TL, BR, threshold):
    ''' 
    HSV版：対象画像の指定箇所を切り抜いてマスク処理した後で比較画像との一致率を算出する
    template    : 比較画像（二値画像）
    image       : 対象画像
    TL          : 切り取り左上座標
    BR          : 切り取り右下座標
    threshold   : 色閾値 [min, max] で指定  
    '''        
    # 対象の切り抜き
    l, t = TL
    r, b = BR
    img_trm = image[t:b, l:r]

    # 閾値を設定
    # リスト形式
    if type(threshold) is list:
        thd_min, thd_max = threshold
    # 色指定
    elif type(threshold) is str:
        thd_min, thd_max = thd_hsv[threshold]  
        
    # RGB -> BGR -> HSV
    bgr_trm = cv2.cvtColor(img_trm, cv2.COLOR_RGB2BGR)
    hsv_trm = cv2.cvtColor(bgr_trm, cv2.COLOR_BGR2HSV)
    
    # 閾値で2値化
    bin_trm = cv2.inRange(hsv_trm, thd_min, thd_max)
    # マスク処理
    msk_trm = cv2.bitwise_and(bin_trm, template) 
        
    # 一致率の算出
    jug = cv2.matchTemplate(msk_trm, template, cv2.TM_CCORR_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
    

    return maxVal



def getNumber(image, TL, BR, image_num, image_unit='nounit', threshold='wht'):
    ''' 
    対象画像の指定箇所の数字を取得する
    image       : 対象画像
    TL          : 切り取り左上座標
    BR          : 切り取り右下座標
    image_num   : 数字画像 [0~9]の順の二値画像リスト
    image_unit  : 単位画像 範囲に単位が含まれる場合は入力 
    threshold   : 色閾値 [min, max] で指定  
    '''    
    # 数字の高さと幅の最大最小を取得
    h_list = [image_num[i].shape[0] for i in range(10)]
    w_list = [image_num[i].shape[1] for i in range(10)]
    h_max, h_min = max(h_list), min(h_list)
    w_max, w_min = max(w_list), min(w_list)
    
    # 閾値を設定
    # リスト形式
    if type(threshold) is list:
        thd_min, thd_max = threshold
    # 色指定
    elif type(threshold) is str:
        thd_min, thd_max = thd_rgb[threshold]  
        
    # 対象の切り抜き
    l, t = TL
    r, b = BR
    img_trm = image[t:b, l:r]
        
    # 閾値で2値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
        
    # 単位画像の入力があった場合
    if type(image_unit) == np.ndarray:
        # 単位の検出
        jug = cv2.matchTemplate(bin_trm, image_unit, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)       
        
        # 単位より左側の数字部分を切り抜き
        left_per = maxLoc[0]
        bin_trm = bin_trm[:, 0:left_per]
                    
    # ラベリング処理
    num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_trm)
    num_labels = num_labels - 1
    stats = np.delete(stats, 0, 0)

    # 記録用リスト    
    num_list = []
    
    for index in range(num_labels):
        x = stats[index][0]
        y = stats[index][1]
        w = stats[index][2]
        h = stats[index][3]
        
        # 高さが小さいものは小数点やノイズ
        if h > h_min*0.9: 
            # 対象を切り取り target
            bin_tmp = bin_trm[y:y+h, x:x+w]
            
            # 対象を黒画像に貼り付け
            bin_tgt = np.zeros((h_max+2, w_max+2), dtype=np.uint8)
            for i in range(h):
                bin_tgt[1+i][1:1+w] = bin_tmp[i]
            
            # 対象の数字を判別する
            num_tgt = 0
            val_tgt = 0 
            
            # 0~9の数字
            for num, bin_num in enumerate(image_num):   
                # 一致率を算出
                jug = cv2.matchTemplate(bin_tgt, bin_num, cv2.TM_CCOEFF_NORMED)
                minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
                
                if maxVal > val_tgt:
                    num_tgt = num
                    val_tgt = maxVal
    
            num_list.append([num_tgt, x])
            
            
    # 記録リストをx座標の大きい順（下の桁から上へ）にソート
    num_list.sort(key=lambda x: x[1], reverse=True) 

    # ソートしたリストを数字に変換
    number = 0
    for i, [num, x] in enumerate(num_list):
        place = 10 ** i     # 桁:place
        number += num * place


    return number



def test():
    ''' 動作テスト '''   
    
    img_path = '.\\capture_image\\image_opening_stage1.png'
    img_path = '.\\capture_image\\image_sub_zones_1.png'
    frame = cv2.imread(img_path)
    
    tmp_path = '.\\pbm\\keyobject\\sign_nice.pbm'
    bin_tmp = cv2.imread(tmp_path, -1)
    
    TL = ( 68, 1016)
    BR = (132, 1048)
    val_rule = matchMaskRGB(bin_tmp, frame, TL, BR, 'wht')
    
    print(val_rule)


    
if __name__ == "__main__":    
    test()
 



