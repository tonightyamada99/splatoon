# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip


# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# 時計
TL_tim = ( 912, 54)
BR_tim = (1008, 99)
# FINISH!
TL_fin = (380, 630)
BR_fin = (690, 720)

# 閾値 threshold
# 一致率
thd_val = 0.9

# RGBの閾値[min, max](0~255, 0~255, 0~255)
thd_rgb = {'blk':[(  0,   0,   0), (128, 128, 128)],
           'wht':[(128, 128, 128), (255, 255, 255)]}

# 比較画像
# 試合開始ナワバリ
bin_259 = cv2.imread('.\\pbm\\time_259.pbm', -1)
# 試合開始ガチルール
bin_459 = cv2.imread('.\\pbm\\time_459.pbm', -1)
# 試合終了
bin_fin = cv2.imread('.\\pbm\\time_fin.pbm', -1)
    


def judgeStartTurf(frame):
    ''' ナワバリ試合開始の判定 '''
    # 一致率算出  
    val = iip.matchRGB(bin_259, frame, TL_tim, BR_tim, 'wht')

    # 閾値以上ならば試合開始
    if val > thd_val:     
        return True    
    else:
        return False



def judgeStartGachi(frame):
    ''' ガチルール試合開始の判定 '''
    # 一致率算出  
    val = iip.matchRGB(bin_459, frame, TL_tim, BR_tim, 'wht')

    # 閾値以上ならば試合開始
    if val > thd_val:     
        return True    
    else:
        return False


def judgeEnd(frame):
    ''' 試合終了の判定 '''
    # 一致率算出  
    val = iip.matchRGB(bin_fin, frame, TL_fin, BR_fin, 'blk')

    # 閾値以上ならば試合開始
    if val > thd_val:     
        return True    
    else:
        return False
    

def test():
    ''' 動作テスト '''   
    img_path = '.\\capture_image\\image_sub_turf_1.png'
    frame = cv2.imread(img_path)
    jug = judgeStartTurf(frame)
    
    # img_path = '.\\capture_image\\image_finish_1.png'
    # frame = cv2.imread(img_path)
    # jug = judgeEnd(frame)
    
    print(jug)

    # プレビュー
    scale = 0.5
    img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
         
    cv2.imshow('Preview', img_rsz)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    

if __name__ == "__main__":    
    test()
 

