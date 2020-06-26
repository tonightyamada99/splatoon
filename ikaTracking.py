# -*- coding: utf-8 -*-

import cv2


# 2値化の閾値(0～255)
threshold_y = 210
threshold_b = 200

def nameBinarization(img_name, player_num):
    ''' 比較用の画像を白黒変換 '''
    if player_num <= 4:
        threshold = threshold_y
    elif player_num >= 5:
        threshold = threshold_b
        
    ret, gray_name = cv2.threshold(img_name, threshold, 255, cv2.THRESH_BINARY)
    
    return gray_name


def name(frame, gray_name, player_num):
    ''' 位置を「名前」で捕捉する '''
    if player_num <= 4:
        threshold = threshold_y
    elif player_num >= 5:
        threshold = threshold_b

    h, w = gray_name.shape
    
    gray_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    ret, gray_frame = cv2.threshold(gray_cv, threshold, 255, cv2.THRESH_BINARY)
    
    jug = cv2.matchTemplate(gray_frame, gray_name, cv2.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)   
    
    TL = maxLoc
    BR = (TL[0] + w, TL[1] + h)
    point_x = int((TL[0] + BR[0]) / 2)
    point_y = int((TL[1] + 44)) # 名前の上端からイカの位置までの距離は44px（FHDでの値）
    
    return point_x, point_y, maxVal
    
            
def testThreshold(img_path, threshold):
    ''' 閾値を調べる '''
    img_read= cv2.imread(img_path)

    img_gray = cv2.cvtColor(img_read, cv2.COLOR_RGB2GRAY)
    ret, img_thresh = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    
    cv2.imshow('Gray Img', img_thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
                    
    
def main():
    ''' メイン処理 '''        
    img_path = 'image_8.png'
    frame = cv2.imread(img_path)

    player_list = [i for i in range(1, 9)]
    
    # 名前の画像をあらかじめ用意しておく
    gray_all = [[]]  # index 0 はダミー
    for player_num in player_list:
        img_tmp = cv2.imread('PL-DAY2_1-1_name_' + str(player_num) + '.png', 0)
        gray_tmp = nameBinarization(img_tmp, player_num)
        gray_all.append(gray_tmp)
        
    # プレビュー画像
    out_frame = frame
    
    # 位置を捕捉
    for player_num in player_list:
        gray_name = gray_all[player_num]
        point_x, point_y, maxVal = name(frame, gray_name, player_num)

        print(player_num, point_x , point_y, maxVal)
        
        # 結果をプレビュー画像に描画
        TL = (point_x - 100, point_y - 44)
        BR = (point_x + 100, point_y - 16)
        
        cv2.circle(out_frame, (point_x, point_y), 2, (255, 255, 0), -1)
        cv2.rectangle(out_frame, TL, BR, (255, 255, 0), 2)
        
    # プレビュー表示
    cv2.imshow('Result Image', out_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()    
    
        
if __name__ == "__main__":
    main()
    