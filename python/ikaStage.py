# -*- coding: utf-8 -*-

import cv2


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# ステージ名の座標
TL_stage = (1500,  972)
BR_stage = (1890, 1053)

# RGBの閾値[min, max](0~255, 0~255, 0~255)
thd_rgb = {'wht':[(224, 224, 224), (255, 255, 255)]}



def getStage(frame):
    ''' ステージ取得 '''
    # ステージ名表示部分の切り取り
    l, t = TL_stage
    r, b = BR_stage
    img_trm = frame[t:b, l:r]
    
    # 白で2値化
    bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])
    
    # 一致率とステージナンバー
    val_stage = 0 
    stage_num = 'nodata'
    
    # 23ステージ分
    for i in range(23):
        # ステージ名画像読み込み
        bin_stage = cv2.imread('.\\pbm\\stage_name_' + str(i) + '.pbm', -1)
        
        # マスク処理
        msk_trm = cv2.bitwise_and(bin_trm, bin_stage)
        
        # ステージ名画像との一致率を算出
        jug = cv2.matchTemplate(msk_trm, bin_stage, cv2.TM_CCORR_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)
        
        # 一致率が最大となるステージを探す
        if maxVal > val_stage:
            stage_num = i
            val_stage = maxVal  
            
            
    return stage_num



def test():
    ''' 動作テスト '''   
    img_path = '.\\capture_image\\image_opening_stage9.png'
    frame = cv2.imread(img_path)
    
    stage_num = getStage(frame)
    print(stage_num)
    
    # ステージデータ
    import csvread
    stage_list = csvread.readAsList('stage.csv')
    
    for i in range(len(stage_list)):
        if stage_num == stage_list[i][0]:
            stage_name = stage_list[i][1]
            break
        
    print(stage_name)
    
    # プレビュー
    scale = 0.5
    img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
         
    cv2.imshow('Preview', img_rsz)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
            

    
if __name__ == "__main__":    
    test()
 



