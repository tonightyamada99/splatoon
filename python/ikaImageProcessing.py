# -*- coding: utf-8 -*-

"""""""""""""""""""""""""""""""""
スプラトゥーン用の画像処理まとめ
作成者：こんやがやまだ
"""""""""""""""""""""""""""""""""

import cv2


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



def matchMask(template, image, TL, BR, threshold):
    ''' 
    対象画像の指定箇所を切り抜いてマスク処理した後で比較画像との一致率を算出する
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
    対象画像の指定箇所を切り抜いてマスク処理した後で比較画像との一致率を算出する
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


def test():
    ''' 動作テスト '''   
    
    img_path = '.\\capture_image\\image_opening_stage1.png'
    img_path = '.\\capture_image\\image_sub_zones_1.png'
    frame = cv2.imread(img_path)
    
    tmp_path = '.\\keyobject\\sign_nice.png'
    img_tmp = cv2.imread(tmp_path)
    bin_tmp = cv2.inRange(img_tmp, thd_rgb['wht'][0], thd_rgb['wht'][1])
         
    
    TL = ( 68, 1016)
    BR = (132, 1048)
    val_rule = matchMask(bin_tmp, frame, TL, BR, 'wht')
    
    print(val_rule)


    
if __name__ == "__main__":    
    test()
 



