# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# 「ル」の字
TL_ru = (914, 150) 
BR_ru = (944, 216) 
# ルール名
TL_rule = ( 830, 290)
BR_rule = (1100, 500)
    
# 閾値 threshold
# 一致率
thd_val = 0.9

# RGBの閾値[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), (128, 128, 128)],
           'wht':[(128, 128, 128), (255, 255, 255)]}

# ルール一覧
rule_list = ['turf', 'zones', 'tower', 'rain', 'clam']

# 「ル」画像
bin_ru = cv2.imread('.\\pbm\\rule.pbm', -1)



def judgeRule(frame):
    ''' ルール表示フレームの判定 '''    
    # 「ル」一致率算出  
    val_ru = iip.matchRGB(bin_ru, frame, TL_ru, BR_ru, 'wht')

    # 閾値以上ならばルール表示
    if val_ru > thd_val:     
        return True    
    else:
        return False



def getRule(frame):
    ''' ルール取得 '''
    # ルール表示部分の切り取り
    l, t = TL_rule
    r, b = BR_rule
    img_trm = frame[t:b, l:r]
    
    # 白で2値化
    bin_trm = cv2.inRange(img_trm, thd_rgb['wht'][0], thd_rgb['wht'][1])
    
    val_rule = 0 
    for rule_name in rule_list:
        # ルール画像読み込み
        img_rname = cv2.imread('.\\pbm\\rule_' + rule_name + '.pbm')
        bin_rname = cv2.inRange(img_rname, thd_rgb['wht'][0], thd_rgb['wht'][1])
        
        # 一致率算出
        jug = cv2.matchTemplate(bin_trm, bin_rname, cv2.TM_CCORR_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
        
        # 一致率が最大のルールを探す
        if maxVal > val_rule:
            rule = rule_name
            val_rule = maxVal
            
            
    return rule



def test():
    ''' 動作テスト '''   
    img_path = '.\\capture_image\\image_opening_stage1.png'
    # img_path = '.\\capture_image\\image_sub_zones_1.png'
    frame = cv2.imread(img_path)
    
    jug_rule = judgeRule(frame)
    print(jug_rule)
    
    if jug_rule == True:
        rule = getRule(frame)
        print(rule)
    
    
    # プレビュー
    scale = 0.5
    img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
         
    cv2.imshow('Preview', img_rsz)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    
if __name__ == "__main__":    
    test()
 



