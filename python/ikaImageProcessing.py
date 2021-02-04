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
           'yel':[( 20, 128, 128), ( 30, 255, 255)],
           'blu':[(125, 128, 128), (135, 255, 255)]}



def convertThreshold(threshold, color_type='RGB'):
    ''' 型を判別して入力を色閾値に変換 '''
    # list型 -> そのまま返す
    cvt_thd = threshold
    
    # string型 -> 閾値取り出し
    if type(threshold) is str:
        # 色空間で場合分け
        if color_type == 'RGB' or color_type == 'rgb':
            cvt_thd = thd_rgb[threshold] 
        elif color_type == 'HSV' or color_type == 'hsv':
            cvt_thd = thd_hsv[threshold]
        

    return cvt_thd



def getMatchValue(template, image, pt1, pt2,
                  threshold='wht', color_type='RGB'):
    ''' 
    対象画像の指定箇所を切り抜いて比較画像との一致率を算出する
    template    : 比較画像（二値画像）
    image       : 対象画像
    pt1         : 切り取り左上座標
    pt2         : 切り取り右下座標
    threshold   : 色閾値 [min, max] で指定  
    color_type  : 二値化する色空間をRGB/HSVで指定
    '''    
    # 閾値を取得
    thd_min, thd_max = convertThreshold(threshold, color_type)    
    
    # 対象の切り抜き
    left,  top    = pt1
    right, bottom = pt2
    img_trm = image[top:bottom, left:right]
    
    # BGR -> HSV
    if color_type == 'HSV' or color_type == 'hsv':
        img_trm = cv2.cvtColor(img_trm, cv2.COLOR_BGR2HSV)
    
    # 閾値で二値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
    # 一致率の算出
    jug = cv2.matchTemplate(bin_trm, template, cv2.TM_CCORR_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
    

    return maxVal



def getMatchValueMask(template, image, pt1, pt2,
                      threshold='wht', color_type='RGB'):
    ''' 
    対象画像の指定箇所を切り抜いてマスク処理した後で比較画像との一致率を算出する
    template    : 比較画像（二値画像）
    image       : 対象画像
    pt1         : 切り取り左上座標
    pt2         : 切り取り右下座標
    threshold   : 色閾値 [min, max] で指定 
    color_type  : 二値化する色空間をRGB/HSVで指定
    '''        
    # 閾値を取得
    thd_min, thd_max = convertThreshold(threshold, color_type)    
    
    # 対象の切り抜き
    left,  top    = pt1
    right, bottom = pt2
    img_trm = image[top:bottom, left:right] 
    
    # BGR -> HSV
    if color_type == 'HSV' or color_type == 'hsv':
        img_trm = cv2.cvtColor(img_trm, cv2.COLOR_BGR2HSV)
        
    # 閾値で2値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
    # マスク処理
    msk_trm = cv2.bitwise_and(bin_trm, template) 
    # 一致率の算出
    jug = cv2.matchTemplate(msk_trm, template, cv2.TM_CCORR_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
    

    return maxVal



def getMostLargeColor(image, pt1, pt2, color_list):
    ''' 
    対象画像の指定箇所で最も面積を占める色を取得する
    image       : 対象画像
    pt1         : 切り取り左上座標
    pt2         : 切り取り右下座標
    color_list  : 候補色リスト string型
    '''        
    # 対象の切り抜き
    left,  top    = pt1
    right, bottom = pt2
    img_trm = image[top:bottom, left:right] 
    # BGR -> HSV
    hsv_trm = cv2.cvtColor(img_trm, cv2.COLOR_BGR2HSV)
        
    # 各色の面積を記録するリスト
    surf_list = []
    
    for color in color_list:
        # 閾値を取得
        thd_min, thd_max = convertThreshold(color, 'HSV')   
        # 基準色で2値化
        bin_trm = cv2.inRange(hsv_trm, thd_min, thd_max)   
        # 抽出された部分の面積を取得
        s = cv2.countNonZero(bin_trm)
        # 辞書に記録
        surf_list.append(s)
        
    # 面積が最も大きかった色を取得
    index = np.argmax(surf_list)
    max_color = color_list[index]
    
    
    return max_color



def getMostMatchImage(image, pt1, pt2, tmp_list, 
                      threshold='wht', color_type='RGB'):
    ''' 
    対象画像の指定箇所に最も一致する画像のインデックスを取得する
    image       : 対象画像
    pt1         : 切り取り左上座標
    pt2         : 切り取り右下座標
    tmp_list    : 候補画像リスト（二値画像）
    '''        
    # 閾値を取得
    thd_min, thd_max = convertThreshold(threshold, color_type) 
    
    # 対象の切り抜き
    left,  top    = pt1
    right, bottom = pt2
    img_trm = image[top:bottom, left:right] 

    # BGR -> HSV
    if color_type == 'HSV' or color_type == 'hsv':
        img_trm = cv2.cvtColor(img_trm, cv2.COLOR_BGR2HSV)
        
    # 閾値で2値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
        
    # 一致率が最も高いものを探す
    val_max = 0
    index = 'nodata'
    for i, template in enumerate(tmp_list):
        # マスク処理
        msk_trm = cv2.bitwise_and(bin_trm, template) 
        # 一致率の算出s
        jug = cv2.matchTemplate(msk_trm, template, cv2.TM_CCORR_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
        
        if maxVal > val_max:
            val_max = maxVal
            index = i
        
    
    return index



def getNumber(image, pt1, pt2, image_num, 
              image_unit='nounit', threshold='wht'):
    ''' 
    対象画像の指定箇所の数字を取得する
    数字のみの認識となるため小数点は返り値を0.1倍などして対応する
    image       : 対象画像
    pt1         : 切り取り左上座標
    pt2         : 切り取り右下座標
    image_num   : 数字画像 [0~9]の順の二値画像リスト
    image_unit  : 単位画像 範囲に単位が含まれる場合は入力 
    threshold   : 色閾値 [min, max] で指定  
    '''    
    # 閾値を取得
    thd_min, thd_max = convertThreshold(threshold)  
    
    # 数字の高さと幅の最大最小を取得
    h_list = [image_num[i].shape[0] for i in range(10)]
    w_list = [image_num[i].shape[1] for i in range(10)]
    h_max, h_min = max(h_list), min(h_list)
    w_max, w_min = max(w_list), min(w_list)
         
    # 対象の切り抜き
    left,  top    = pt1
    right, bottom = pt2
    img_trm = image[top:bottom, left:right] 
        
    # 閾値で2値化
    bin_trm = cv2.inRange(img_trm, thd_min, thd_max)
        
    # 単位画像の入力があった場合
    if type(image_unit) == np.ndarray:
        # 単位の検出
        jug = cv2.matchTemplate(bin_trm, image_unit, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)       
        
        # 単位より左側の数字部分を切り抜き
        left_unit = maxLoc[0]
        bin_trm = bin_trm[:, 0:left_unit]
                    
    # ラベリング処理
    num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_trm)
    num_labels = num_labels - 1
    stats = np.delete(stats, 0, 0)

    # 認識した数字の記録リスト    
    num_list = []
    
    for index in range(num_labels):
        x = stats[index][0]
        y = stats[index][1]
        w = stats[index][2]
        h = stats[index][3]
        
        # 高さが小さいものは小数点やノイズ
        if h > h_min*0.9: 
            # 対象を切り取り
            bin_tmp = bin_trm[y:y+h, x:x+w]
            
            # 対象を黒画像に貼り付け target
            # 数字ごとの大きさの違いに対応するため
            bin_tgt = np.zeros((h_max+2, w_max+2), dtype=np.uint8)
            bin_tgt[1:1+h, 1:1+w] = bin_tmp
            
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
    
            # リストに記録
            num_list.append([num_tgt, x])
            
            
    # 記録リストをx座標の大きい順（下の桁から上へ）にソート
    num_list.sort(key=lambda x: x[1], reverse=True) 

    # ソートしたリストを数字に変換
    # 桁の小さい順に並んでいるので(数字)×10^(インデックス)で変換できる
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
    
    tmp_path = '.\\pbm\\sign_nice.pbm'
    bin_tmp = cv2.imread(tmp_path, -1)
    
    TL = ( 68, 1016)
    BR = (132, 1048)
    val_rule = getMatchValueMask(bin_tmp, frame, TL, BR)
    
    print(val_rule)


    
if __name__ == "__main__":    
    test()
 



